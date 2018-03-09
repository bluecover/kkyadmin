#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/30/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from behaviors import BuildWordhourData
import re
from errors import PermissionDeny


class CourierWorkhourContent(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'ScheduleRead' in self.current_user['privileges']:
            raise PermissionDeny()

        area = self.get_argument('area', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        campus = self.get_argument('campus', '')
        if campus == u'全部校区':
            campus = None

        data = yield BuildWordhourData().BuildWorkhourOfArea(
            self.current_user,
            area,
            province,
            city,
            campus
        )

        self.render('work_hour.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'ScheduleUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        area = self.get_argument('area', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        campus = self.get_argument('campus', '')

        courier_schedules = {}
        for k,v in self.request.arguments.items():
            m = re.findall('sched_(.*)_(.*)_(.*)', k)
            if not m or len(m[0]) != 3:
                continue
            courier_id = m[0][0]
            sched = courier_schedules.setdefault(courier_id, [])
            sched.append(
                {
                    'start': int(m[0][1]),
                    'end': int(m[0][2])
                }
            )

        yield BuildWordhourData().UpdateSchedules(campus, courier_schedules)

        data = yield BuildWordhourData().BuildWorkhourOfArea(
            self.current_user,
            area,
            province,
            city,
            campus
        )

        self.render('work_hour.html', data=data)
