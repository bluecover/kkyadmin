#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/30/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
import json
from BuildAreaData import BuildAreaData
from bson import ObjectId
from Utils import Utils


class BuildTaskData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kw['user'])
        data = {
            'filters': {
                'types': {
                        'task_id': u'任务ID',
                        'courier_name': u'速递员姓名',
                        'courier_mobile': u'速递员手机号',
                        'courier_id': u'速递员ID'
                },
                'status':{
                    'waiting': u'等待分配',
                    'dispatched': u'已分配',
                    'processing': u'正在配送',
                    'done': u'已完成'
                }
            },
            'table_src': 'task_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'task_id':
            condition['_id'] = ObjectId(kw['filter_value'])
        if kw['filter_type'] == 'courier_id':
            condition['courier_mobile'] = ObjectId(kw['filter_value'])
        if kw['filter_type'] == 'courier_name':
            condition['courier_name'] = kw['filter_value'].encode('utf8')
        if kw['filter_type'] == 'courier_mobile':
            condition['courier_mobile'] = kw['filter_value']
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

        tasks, tasks_count = yield self.FindTasksByArea(
            skip=skip,
            limit=limit,
            region=kw['area'],
            province=kw['province'],
            city=kw['city'],
            school=kw['campus'],
            extra_condition=condition
        )

        datas = []
        for t in tasks:
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': t.get('courier_name', '')
                    },
                    {
                        'type': 'text',
                        'value': t['shop']['name']
                    },
                    {
                        'type': 'text',
                        'value': t['district_name']
                    },
                    {
                        'type': 'text',
                        'value': len(t['subtasks'])
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(t['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().TaskStatusToChinese(t['status']),
                        'color': ConvertText().TaskStatusColor(t['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/task_detail?id=%s")' % str(t['_id'])
                    }
                ]
            )
        data = {
            'thead': [u'速递员姓名', u'取货商家', u'归属校区', u'订单数', u'创建时间', u'状态', u'操作'],
            'datas': datas,
            'count': tasks_count
        }
        raise gen.Return(data)


    @gen.coroutine
    def FindTasksByArea(self, skip=None, limit=None, region=None, province=None, city=None, school=None,
                        extra_condition={}):
        school_condition = yield Utils().BuildSchoolCondition(region, province, city, school, 'district_id')
        sort_condition = [
            ('created_time', -1)
        ]
        task_condition = dict(school_condition.items() + extra_condition.items())
        query = self.task_model.find(task_condition)
        tasks_count = yield query.count()
        if skip is not None and limit is not None:
            tasks = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)
        else:
            tasks = yield query.sort(sort_condition).to_list(None)

        raise gen.Return((tasks, tasks_count))


    @gen.coroutine
    def BuildTaskDetail(self, task_id):
        task = yield self.task_model.GetTaskFromId(task_id)
        data = {
            'task': {
                'status_text': ConvertText().TaskStatusToChinese(task['status']),
                '_id': task_id,
                'created_time': ConvertText().TimestampToText(task.get('created_time', 0)),
                'process_time': ConvertText().TimestampToText(task.get('dispatched_time', 0)),
                'finish_time': ConvertText().TimestampToText(task.get('done_time', 0)),
                'courier': {
                    'name': task.get('courier_name', ''),
                    'mobile': task.get('courier_mobile', ''),
                    '_id': task.get('courier_id', '')
                },
                'shop': {
                    'name': '',
                    'mobile': '',
                    'address': ''
                },
                'orders': []
            }
        }

        shop = task.get('shop')
        if shop:
            data['task']['shop']['name'] = shop.get('name', '')
            data['task']['shop']['mobile'] = shop.get('mobile', '')
            data['task']['shop']['address'] = shop.get('address', '')

        for subtask_id in task['subtasks']:
            subtask = yield self.subtask_model.GetSubtaskFromId(subtask_id)
            order_id = subtask['express_no']
            order = yield self.order_model.GetOrderFromId(ObjectId(order_id))
            if order:
                data['task']['orders'].append(
                    {
                        '_id': order['_id'],
                        'address': order['receiving']['address'],
                        'successTime': ConvertText().TimestampToText(order.get('confirm_time', 0)),
                        'total': (order['total_price'] + order['discount_price'] + order['delivery_price']) / 100.0,
                        'discount': order['discount_price'] / 100.0,
                        'pay': order['pay_total'] / 100.0
                    }
                )

        raise gen.Return(data)
