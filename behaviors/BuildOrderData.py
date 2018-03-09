#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/26/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
from BuildAreaData import BuildAreaData
import json
from bson import ObjectId
from BuildShopData import BuildShopData
from Utils import Utils


class BuildOrderData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kwargs):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kwargs['user'])
        data = {
            'filters': {
                'types': {
                    'name': u'收货人姓名',
                    'address': u'收货地址',
                    'user_mobile': u'用户手机号',
                    'receive_mobile': u'收货人手机号',
                    'courier_name': u'速递员姓名',
                    'courier_mobile': u'速递员手机号',
                    'id': u'订单ID'
                },
                'status': {
                    'unpaid': u'未支付',
                    'paid': u'已支付',
                    'sending': u'配送中',
                    'uncomment': u'已收货',
                    'done': u'已完成',
                    'refunded': u'已退款',
                    'cancel': u'已取消'
                }
            },
            'table_src': 'order_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'name':
            condition['receiving.name'] = kw['filter_value']
        if kw['filter_type'] == 'address':
            condition['receiving.address'] = kw['filter_value']
        if kw['filter_type'] == 'receive_mobile':
            condition['receiving.mobile'] = kw['filter_value']
        if kw['filter_type'] == 'user_mobile':
            user = yield self.user_model.find_one({ 'mobile': kw['filter_value'] })
            condition['user_id'] = user['_id'] if user else ''
        if kw['filter_type'] == 'courier_name':
            condition['courier_name'] = kw['filter_value']
        if kw['filter_type'] == 'courier_mobile':
            condition['courier_mobile'] = kw['filter_value']
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

        orders, orders_count = yield self.FindOrdersByArea(
            skip=skip,
            limit=limit,
            region=kw['area'],
            province=kw['province'],
            city=kw['city'],
            school=kw['campus'],
            extra_condition=condition
        )

        datas = []
        for o in orders:
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': o['receiving']['name']
                    },
                    {
                        'type': 'text',
                        'value': o['receiving']['address']
                    },
                    {
                        'type': 'text',
                        'value': o.get('school', '')
                    },
                    {
                        'type': 'text',
                        'value': (o['items_price'] + o['delivery_price'])/100.0
                    },
                    {
                        'type': 'text',
                        'value': o['pay_total']/100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(o['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().OrderStatusToChinese(o['status']),
                        'color': ConvertText().OrderStatusColor(o['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/order_detail?id=%s")' % str(o['_id'])
                    }
                ]
            )
        data = {
            'thead': [u'收货人姓名', u'收货地址', u'归属校区', u'订单总价', u'实际支付', u'下单时间', u'状态', u'操作'],
            'datas': datas,
            'count': orders_count
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildOrderDetail(self, order):
        user = yield self.user_model.GetUserFromId(order['user_id'])
        data = {
            'order': {
                '_id': order['_id'],
                'status_text': ConvertText().OrderStatusToChinese(order['status']),
                'receiver': {
                    'name': order['receiving']['name'],
                    'mobile': order['receiving']['mobile'],
                    'address': order['receiving']['address'],
                    'account_mobile': user['mobile']
                },
                'user': {
                    'created_time': ConvertText().TimestampToText(user['created_time'])
                },
                'goods': [
                    {
                        'name': item.get('name', ''),
                        'count': item['num'],
                        'price': item['price']/100.0,
                        '_id': item['_id']
                    } for item in order['items']
                ],
                'price': {
                    'total': (order['total_price'] + order['discount_price'] + order['delivery_price'])/100.0,
                    'discount': order['discount_price']/100.0,
                    'pay': order['pay_total']/100.0
                },
                'courier': {
                    'name': order.get('courier_name', ''),
                    'mobile': order.get('courier_mobile', ''),
                    '_id': order.get('courier_id', '')
                },
                'createdTime': ConvertText().TimestampToText(order.get('created_time', 0)),
                'paidTime': ConvertText().TimestampToText(order.get('paid_time', 0)),
                'sendTime': ConvertText().TimestampToText(order.get('send_time', 0)),
                'receiveTime': ConvertText().TimestampToText(order.get('confirm_time', 0)),
                'successTime': ConvertText().TimestampToText(order.get('done_time', 0)),
                'note': order.get('remark', ''),
                'evaluation': {
                    'level': order.get('comment_type', ''),
                    'comment': order.get('comment', '')
                },
                'area': order.get('region', ''),
                'province': order.get('province', ''),
                'city': order.get('city', ''),
                'campus':order.get('school', ''),
                'express_id': order.get('express_id', '')
            }
        }

        refund_reason = 'do_not_want'
        refund_detail = ''
        refund_record = yield self.order_refund_model.GetRecord(order['_id'])
        if refund_record:
            refund_reason = refund_record['reason']
            refund_detail = refund_record['detail']
        refund_reason_candidates = self.order_refund_model.CandidateReasons()
        refund_reasons = [
            {
                'key': r,
                'text': ConvertText().OrderRefundReasonToChinese(r),
                'selected': True if refund_reason == r else False
            } for r in refund_reason_candidates
        ]
        data['order']['refund_reasons'] = refund_reasons
        data['order']['refund_reason'] = refund_reason
        data['order']['refund_detail'] = refund_detail

        hurry_reason = 'no_available_courier'
        hurry_reason_candidates = self.order_hurry_model.CandidateReasons()
        hurry_reasons = [
            {
                'key': r,
                'text': ConvertText().OrderHurryReasonToChinese(r),
                'selected': True if hurry_reason == r else False
            } for r in hurry_reason_candidates
        ]
        data['order']['hurry_reasons'] = hurry_reasons

        order_hurry_records = yield self.order_hurry_model.GetRecords(order['_id'])
        hurry_records = [
            {
                'reason': ConvertText().OrderHurryReasonToChinese(r['reason']),
                'detail': r.get('detail', ''),
                'time': ConvertText().TimestampToText(r['created_time'])
            } for r in order_hurry_records
        ]
        data['order']['hurry_records'] = {
            'thead': [u'时间', u'原因', u'细节'],
            'datas': hurry_records
        }

        pay_id = order.get('pay_id')
        if pay_id:
            pay_record = yield self.pay_model.find_one({'_id': pay_id})
            data['order']['pay'] = {
                'method': ConvertText().PayMethodToChinese(pay_record['platform']),
                'pay_no': pay_record.get('trade_no', '')
            }

        raise gen.Return(data)


    @gen.coroutine
    def FindOrdersByArea(self, skip=None, limit=None, region=None, province=None, city=None, school=None,
                         extra_condition={}):
        school_condition = yield Utils().BuildSchoolCondition(region, province, city, school)
        order_condition = dict(school_condition.items() + extra_condition.items())
        sort_condition = [
            ('created_time', -1)
        ]
        query = self.order_model.find(order_condition)
        orders_count = yield query.count()
        if skip is not None and limit is not None:
            orders = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)
        else:
            orders = yield query.sort(sort_condition).to_list(None)

        raise gen.Return((orders, orders_count))
