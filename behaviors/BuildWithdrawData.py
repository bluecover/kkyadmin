#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/7/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
from bson import ObjectId
from BuildAreaData import BuildAreaData
import json


class BuildWithdrawData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kw['user'])
        data = {
            'filters': {
                'types': {
                    'name': u'姓名',
                    'id': u'提现ID'
                },
                'status': {
                    'processed': u'已处理',
                    'unprocessed': u'未处理',
                }
            },
            'table_src': 'withdraw_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'name':
            condition['name'] = kw.get('filter_value')
        if kw['filter_type'] == 'id':
            condition['_id'] = ObjectId(kw['filter_value'])
        status = kw.get('filter_status', None)
        if status:
            condition['status'] = status

        if kw['filter_time_start']:
            condition['created_time'] = { '$gte': kw['filter_time_start'] }
        if kw['filter_time_end']:
            condition_time = condition.setdefault('created_time', {})
            condition_time['$lte'] = kw['filter_time_end']

        PAGE_SIZE = 20
        page = kw['page'] - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE

        withdraws, withdraws_count = yield self.FindWithdrawsByArea(
            skip=skip,
            limit=limit,
            region=kw['area'],
            province=kw['province'],
            city=kw['city'],
            school=kw['campus'],
            extra_condition=condition
        )

        datas = []
        for w in withdraws:
            school_name = ''
            courier = yield self.courier_model.GetCourierFromId(w['courier_id'])
            if courier:
                school = yield self.school_model.GetSchoolFromId(courier['district_id'])
                if school:
                    school_name = school['name']
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': w['name']
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawTypeToChinese(w['account_type'])
                    },
                    {
                        'type': 'text',
                        'value': school_name
                    },
                    {
                        'type': 'text',
                        'value': w['money']/100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(w['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().WithdrawStatusToChinese(w['status']),
                        'color': ConvertText().WithdrawStatusColor(w['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/withdraw_detail?id=%s")' % str(w['_id'])
                    }
                ]
            )
        data = {
            'thead': [u'姓名', u'提现方式', u'归属校区', u'金额', u'提现时间', u'状态', u'操作'],
            'datas': datas,
            'count': withdraws_count
        }
        raise gen.Return(data)

    @gen.coroutine
    def FindWithdrawsByArea(self, skip=None, limit=None, region=None, province=None, city=None, school=None,
                            extra_condition={}):
        if region == u'全部大区':
            region = None
        if province == u'全部省份':
            province = None
        if city == u'全部城市':
            city = None
        if school == u'全部校区':
            school = None
        schools, _ = yield self.school_model.GetSchoolsAndCountFromArea(
            region=region,
            province=province,
            city=city,
            school=school
        )
        school_ids = [s['_id'] for s in schools]
        school_condition = {
            'school_id': {
                '$in': school_ids
            }
        }

        withdraw_condition = dict(school_condition.items() + extra_condition.items())
        sort_condition = [
            ('created_time', -1)
        ]
        query = self.withdraw_model.find(withdraw_condition)
        count = yield query.count()
        if skip is not None and limit is not None:
            results = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)
        else:
            results = yield query.sort(sort_condition).to_list(None)
        raise gen.Return((results, count))

    @gen.coroutine
    def BuildWithdrawDetail(self, withdraw_id):
        w = yield self.withdraw_model.GetWithdrawFromId(withdraw_id)
        courier = yield self.courier_model.GetCourierFromId(w['courier_id'])
        withdraw_data = {
            'status_text': ConvertText().WithdrawStatusToChinese(w['status']),
            'courier': courier.get('name', ''),
            '_id': w['_id'],
            'method': ConvertText().WithdrawTypeToChinese(w['account_type']),
            'created_time': ConvertText().TimestampToText(w['created_time']),
            'price': w['money']/100.0,
            'alipay': {
                'name': w.get('name', ''),
                'account': w.get('account', '')
            },
            'bank': {
                'bank': w.get('bank_name', ''),
                'number': w.get('account', ''),
                'province': w.get('bank_province_city', ''),
                'city': w.get('bank_province_city', ''),
                'subbranch': w.get('bank_branch', '')
            }
        }
        raise gen.Return(withdraw_data)
