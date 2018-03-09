#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from Behavior import Behavior
from tornado import gen
import json
from BuildAreaData import BuildAreaData
from bson import ObjectId
from behaviors import ConvertText


class BuildExpendData(Behavior):
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
            'extra_btns': [
                {
                    'text': u'生成表格',
                    'href': '/expenses_export'
                }
            ],
            'table_src': 'expenses_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'name':
            condition['courier_name'] = kw.get('filter_value')
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

        expends, expends_count = yield self.FindExpendsByArea(
            skip=skip,
            limit=limit,
            region=kw['area'],
            province=kw['province'],
            city=kw['city'],
            school=kw['campus'],
            extra_condition=condition
        )

        datas = []
        for e in expends:
            withdraw = yield self.withdraw_model.GetWithdrawFromId(e['withdraw_id'])
            school_name = ''
            courier = yield self.courier_model.GetCourierFromId(e['courier_id'])
            if courier:
                school = yield self.school_model.GetSchoolFromId(courier['district_id'])
                if school:
                    school_name = school['name']
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': e['courier_name']
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawTypeToChinese(withdraw['account_type'])
                    },
                    {
                        'type': 'text',
                        'value': school_name
                    },
                    {
                        'type': 'text',
                        'value': e['real_amount']/100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(withdraw['created_time'])
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(e['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().WithdrawStatusToChinese(e['status']),
                        'color': ConvertText().WithdrawStatusColor(e['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/expenses_detail?id=%s")' % str(e['_id'])
                    }
                ]
            )

        data = {
            'thead': ['姓名', '提现方式', '归属校区', '支出金额', '提现时间', '创建时间', '状态', '操作'],
            'datas': datas,
            'count': expends_count
        }

        raise gen.Return(data)


    @gen.coroutine
    def FindExpendsByArea(self, skip=None, limit=None, region=None, province=None, city=None, school=None,
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

        expend_condition = dict(school_condition.items() + extra_condition.items())
        sort_condition = [
            ('created_time', -1)
        ]
        query = self.expend_model.find(expend_condition)
        count = yield query.count()
        if skip is not None and limit is not None:
            results = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)
        else:
            results = yield query.sort(sort_condition).to_list(None)
        raise gen.Return((results, count))


    @gen.coroutine
    def BuildExpendDetail(self, expend_id):
        expd = yield self.expend_model.GetExpendFromId(expend_id)
        withdraw = yield self.withdraw_model.GetWithdrawFromId(expd['withdraw_id'])
        withdraw_data = {
            'expenses': {
                'status_text': ConvertText().WithdrawStatusToChinese(expd['status']),
                'status_color': ConvertText().WithdrawStatusColor(expd['status']),
                'courier': expd.get('courier_name', ''),
                'courier_id': expd.get('courier_id', ''),
                '_id': expd['_id'],
                'method': ConvertText().WithdrawTypeToChinese(withdraw['account_type']),
                'created_time': ConvertText().TimestampToText(expd['created_time']),
                'withdraw_amount': expd['withdraw_amount']/100.0,
                'fine_amount': expd['fine_amount']/100.0,
                'real_amount': expd['real_amount']/100.0,
                'alipay': {
                    'name': withdraw.get('name', ''),
                    'account': withdraw.get('account', '')
                },
                'bank': {
                    'bank': withdraw.get('bank_name', ''),
                    'number': '' if withdraw['account_type'] != 'bank' else withdraw.get('account', ''),
                    'province': withdraw.get('bank_province_city', ''),
                    'city': withdraw.get('bank_province_city', ''),
                    'subbranch': withdraw.get('bank_branch', '')
                }
            }
        }
        raise gen.Return(withdraw_data)
