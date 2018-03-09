#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/29/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
import json
from BuildAreaData import BuildAreaData
import datetime
import time
from bson import ObjectId
from Utils import Utils


class BuildCourierData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kw['user'])
        data = {
            'filters': {
                'types': {
                        'courier_name': u'速递员姓名',
                        'courier_mobile': u'速递员手机号'
                },
                'status':{
                    'unsubmitted': u'未提交资料',
                    'verifying': u'审核中',
                    'failed': u'审核失败',
                    'verified': u'已审核',
                    'locked': u'锁定',
                }
            },
            'table_src': 'courier_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)

    @gen.coroutine
    def BuildTableContent(self, **kw):
        region = kw['area']
        if region == u'全部大区':
            region = None
        province = kw['province']
        if province == u'全部省份':
            province = None
        city = kw['city']
        if city == u'全部城市':
            city = None
        campus = kw['campus']
        if campus == u'全部校区':
            campus = None

        PAGE_SIZE = 20
        page = kw['page'] - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE

        other_condition = {}
        if kw['filter_type'] == 'courier_name':
            other_condition['name'] = kw.get('filter_value')
        if kw['filter_type'] == 'courier_mobile':
            other_condition['mobile'] = kw.get('filter_value')
        status = kw.get('filter_status', None)
        if status:
            other_condition['status'] = status

        if kw['filter_time_start']:
            other_condition['created_time'] = { '$gte': kw['filter_time_start'] }
        if kw['filter_time_end']:
            condition_time = other_condition.setdefault('created_time', {})
            condition_time['$lte'] = kw['filter_time_end']


        school_condition = yield Utils().BuildSchoolCondition(region, province, city, campus, 'district_id')
        if not school_condition:
            school_condition = {
                'district_id': { '$exists': True }
            }

        condition = dict(school_condition.items() + other_condition.items())

        query = self.courier_model.find(condition)
        couriers_count = yield query.count()
        couriers = yield query.limit(limit).skip(skip).to_list(None)

        datas = []
        for c in couriers:
            school = yield self.school_model.GetSchoolFromId(c['district_id'])
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': c.get('name', '')
                    },
                    {
                        'type': 'text',
                        'value': c.get('mobile', '')
                    },
                    {
                        'type': 'text',
                        'value': school['name'] if school else ''
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(c['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().CourierStatusToChinese(c['status']),
                        'color': ConvertText().CourierStatusColor(c['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/courier_detail?id=%s")' % str(c['_id'])
                    }
                ]
            )

        data = {
            'thead': [u'姓名', u'手机', u'校区', u'时间', u'状态', u'操作'],
            'datas': datas,
            'count': couriers_count
        }
        raise gen.Return(data)

    @gen.coroutine
    def BuildCourierDeatil(self, courier, current_user):
        week_date_start = self.GetWeekStartDate('this')
        week_date_end = week_date_start + datetime.timedelta(days=7)
        week_timestamp_start = int(time.mktime(week_date_start.timetuple()))
        week_timestamp_end = int(time.mktime(week_date_end.timetuple()))
        schedules = yield self.schedule_model.GetCourierSchedulesInInterval(
            courier['_id'], week_timestamp_start, week_timestamp_end)
        sched_result = {
            '6:00-12:00': [0,0,0,0,0,0,0],
            '12:00-18:00': [0,0,0,0,0,0,0],
            '18:00-24:00': [0,0,0,0,0,0,0]
        }
        for sched in schedules:
            start = sched['start']
            sched_datetime = datetime.datetime.fromtimestamp(start)
            weekday = sched_datetime.weekday()
            time_index = self.HourToIntervalIndex(sched_datetime.hour)
            if time_index == 0:
                sched_result['6:00-12:00'][weekday] = 1
            elif time_index == 1:
                sched_result['12:00-18:00'][weekday] = 1
            elif time_index == 2:
                sched_result['18:00-24:00'][weekday] = 1

        data = {
            'courier': {
                'name': courier.get('name', ''),
                'status': courier['status'],
                'status_text': ConvertText().CourierStatusToChinese(courier['status']),
                '_id': courier['_id'],
                'school': courier.get('school', ''),
                'mobile': courier.get('mobile', ''),
                'birthday': courier.get('birthday', ''),
                'edu_start_year': courier.get('graduate_year', ''),
                'QQ': courier.get('qq', ''),
                'created_time': ConvertText().TimestampToText(courier.get('created_time', 0)),
                'balance': courier.get('balance', 0) / 100.0,
                'position': courier.get('location', [0,0])
            },
            'working_hours': sched_result
        }

        photo_id = courier.get('certificate_image', None)
        if photo_id:
            data['courier']['photo'] = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(photo_id) + '.jpg';
        else:
            data['courier']['photo'] = ''

        area_full = yield BuildAreaData().BuildAreasWithSchools(current_user)
        school = yield self.school_model.GetSchoolFromId(courier['district_id'])
        data_areas = {
            'full': json.dumps(area_full),
            'choosed': json.dumps(
                {
                    'area': school.get('region', ''),
                    'province': school.get('province', ''),
                    'city': school.get('city', ''),
                    'campus': school.get('name', '')
                }
            )
        }
        data['areas'] = data_areas

        raise gen.Return(data)


    def HourToIntervalIndex(self, hour):
        return [
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, # 00:00 ~ 12:00
            1, 1, 1, 1, 1, 1,                   # 12:00 ~ 18:00
            2, 2, 2, 2, 2, 2                    # 18:00 ~ 24:00
        ][hour]


    def IntervalIndexToHour(self, index):
        return {
            0: (7, 12),
            1: (12, 18),
            2: (18, 24)
        }.get(index)


    def GetWeekStartDate(self, week):
        today = datetime.date.today()
        week_start_date = today - datetime.timedelta(days=today.weekday())
        if week == 'next':
            week_start_date += datetime.timedelta(days=7)
        return week_start_date

    @gen.coroutine
    def BuildCourierAccountData(self, courier_id):
        courier = yield self.courier_model.GetCourierFromId(courier_id)
        fines, _ = yield self.fine_model.GetFinesAndCountFromCourierId(courier_id, skip=0, limit=10)
        expends, _ = yield self.expend_model.GetExpendsAndCountFromCourierId(courier_id, skip=0, limit=10)

        withdraw_expend_data = []
        for expend in expends:
            withdraw = yield self.withdraw_model.GetWithdrawFromId(expend['withdraw_id'])
            withdraw_expend_data.append(
                [
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawTypeToChinese(withdraw['account_type'])
                    },
                    {
                        'type': 'price',
                        'value': expend['withdraw_amount']/100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(withdraw['created_time'])
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawStatusToChinese(expend['status']),
                    },
                    {
                        'type': 'price',
                        'value': expend['real_amount']/100.0
                    }
                ]
            )

        data = {
            'courier': {
                '_id': courier_id,
                'name': courier.get('name', ''),
                'amount': courier.get('balance', 0) / 100.0,
                'debt': courier.get('debt', 0) / 100.0,
                'status_text': ConvertText().CourierAccountStatusToChinese(courier.get('account_status', ''))
            },
            'withholding': {
                'thead': ['扣款金额', '扣款时间', '扣款说明'],
                'datas': [
                    [
                        {
                            'type': 'price',
                            'value': fine['amount'] / 100.0
                        },
                        {
                            'type': 'text',
                            'value': ConvertText().TimestampToText(fine['created_time'])
                        },
                        {
                            'type': 'text',
                            'value': fine.get('description', '')
                        }
                    ] for fine in fines
                ]
            },
            'withdraw': {
                'thead': ['提现方式', '金额', '提现时间', '状态', '实际打款'],
                'datas': withdraw_expend_data
            }
        }

        raise gen.Return(data)
