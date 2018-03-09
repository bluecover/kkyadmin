#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/30/15'


from Behavior import Behavior
from tornado import gen
import json
from BuildAreaData import BuildAreaData
import datetime
import time
from bson import ObjectId


class BuildWordhourData(Behavior):
    @gen.coroutine
    def BuildWorkhourOfArea(self, user, region=None, province=None, city=None, school=None):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(user)
        choosed = {
            'region': region,
            'province': province,
            'city': city,
            'school': school
        }
        if not choosed['school']:
            choosed = self._GetFirstSchool(areas_with_schools)

        workhours = yield self._BuildWorkhourOfSchool(choosed)

        data = {
            'working_hours': workhours,
            'areas': {
                'full': json.dumps(areas_with_schools),
                'choosed': json.dumps(
                    {
                        'area': choosed.get('region', ''),
                        'province': choosed.get('province', ''),
                        'city': choosed.get('city', ''),
                        'campus': choosed.get('school', '')
                    }
                )
            }
        }

        raise gen.Return(data)


    def _GetFirstSchool(self, areas):
        first = {}
        for area in areas:
            region_name = area['n']
            if region_name == u'全部大区':
                continue
            first['region'] = region_name
            for province in area['d']:
                province_name = province['n']
                if province_name == u'全部省份':
                    continue
                first['province'] = province_name
                for city in province['d']:
                    city_name = city['n']
                    if city_name == u'全部城市':
                        continue
                    first['city'] = city_name
                    for school in city['d']:
                        school_name = school['n']
                        if school_name == u'全部校区':
                            continue
                        first['school'] = school_name
                        return first
        return first

    @gen.coroutine
    def _BuildWorkhourOfSchool(self, choosed):
        school = yield self.school_model.GetSchoolFromName(choosed['school'])
        couriers = yield self.courier_model.GetCouriersFromDistrictId(school['_id'])
        week_date_start = self.GetWeekStartDate('this')
        week_date_end = week_date_start + datetime.timedelta(days=7)
        week_timestamp_start = int(time.mktime(week_date_start.timetuple()))
        week_timestamp_end = int(time.mktime(week_date_end.timetuple()))

        interval_schedules = [
            [ [],[],[],[],[],[],[] ],
            [ [],[],[],[],[],[],[] ],
            [ [],[],[],[],[],[],[] ]
        ]

        for c in couriers:
            schedules = yield self.schedule_model.GetCourierSchedulesInInterval(
                c['_id'],
                week_timestamp_start,
                week_timestamp_end
            )

            for interval_index, interval_list in enumerate(interval_schedules):
                interval = self.IntervalIndexToHour(interval_index)
                interval_start = interval[0]
                interval_end = interval[1]
                for weekday, weekday_list in enumerate(interval_list):
                    hour_start = week_timestamp_start + (weekday*24 + interval_start) * 3600
                    hour_end   = week_timestamp_start + (weekday*24 + interval_end) * 3600
                    is_working = False
                    for sched in schedules:
                        if sched['start'] == hour_start and sched['end'] == hour_end:
                            is_working = True
                            break
                    weekday_list.append(
                        {
                            'name': c['name'],
                            'arg_name': 'sched_' + str(c['_id']) + '_' + str(hour_start) + '_' + str(hour_end),
                            'on': is_working
                        }
                    )

        schedule_data = {
            '6:00-12:00': interval_schedules[0],
            '12:00-18:00': interval_schedules[1],
            '18:00-24:00': interval_schedules[2]
        }
        raise gen.Return(schedule_data)


    def IntervalIndexToHour(self, index):
        return {
            0: (7, 12),
            1: (12, 18),
            2: (18, 24)
        }.get(index)


    def HourToIntervalIndex(self, hour):
        return [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # 00:00 ~ 12:00
            1, 1, 1, 1, 1, 1,                   # 12:00 ~ 18:00
            2, 2, 2, 2, 2, 2                    # 18:00 ~ 24:00
        ][hour]


    def GetWeekStartDate(self, week):
        today = datetime.date.today()
        week_start_date = today - datetime.timedelta(days=today.weekday())
        if week == 'next':
            week_start_date += datetime.timedelta(days=7)
        return week_start_date

    @gen.coroutine
    def UpdateSchedules(self, school, courier_schedules):
        school = yield self.school_model.GetSchoolFromName(school)
        school_couriers = yield self.courier_model.GetCouriersFromDistrictId(school['_id'])
        school_courier_ids = [ c['_id'] for c in school_couriers ]
        week_date_start = self.GetWeekStartDate('this')
        week_date_end = week_date_start + datetime.timedelta(days=7)
        week_timestamp_start = int(time.mktime(week_date_start.timetuple()))
        week_timestamp_end = int(time.mktime(week_date_end.timetuple()))

        # Clear all current schedules.
        remove_condition = {
            'courier': { '$in': school_courier_ids },
            'start': {
                '$gte': week_timestamp_start
            },
            'end': {
                '$lte': week_timestamp_end
            }
        }
        yield self.schedule_model.remove(remove_condition)

        # Set new schedules.
        for courier, schedules in courier_schedules.items():
            courier_id = ObjectId(courier)
            for sched in schedules:
                sched_data = {
                    'courier': courier_id,
                    'start': sched['start'],
                    'end': sched['end']
                }
                yield self.schedule_model.insert(sched_data)
