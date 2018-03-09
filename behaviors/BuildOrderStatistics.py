#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/22/15'


from Behavior import Behavior
from tornado import gen
import json
from BuildAreaData import BuildAreaData


REQUEST_ORDER_STATUS = ['paid', 'sending', 'uncomment', 'done', 'cancel', 'refunded'] # 请求单量
PAID_ORDER_STATUS = ['paid', 'sending', 'uncomment', 'done']    # 支付单量
SCHEDULED_ORDER_STATUS = ['sending', 'uncomment', 'done']       # 调度单量
DONE_ORDER_STATUS = ['uncomment', 'done']                       # 完成单量


def CountOrderStatus(status, record):
    count = 0
    for s in status:
        count += record.get(s, 0)
    return count


class BuildOrderStatistics(Behavior):
    @gen.coroutine
    def BuildOrderStatisticsOfRegion(self, user, region, province, city, school_name, page=1):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(user)

        PAGE_SIZE = 20
        page = page - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE

        if school_name != u'全部校区':
            school = yield self.school_model.GetSchoolFromName(school_name)
            condition = {
                'school_id': school['_id']
            }
        else:
            condition = {
                'region': region,
                'province': province,
                'city': city,
                'school_name': school_name
            }

        sort_condition = [
            ('date', -1)
        ]
        query = self.order_statistics.find(condition)
        record_count = yield query.count()
        order_records = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)

        order_date = []
        order_count = []
        paid_order_count = []
        for o in order_records:
            order_date.append(o['date'][4:].encode('utf8'))
            paid_order_count.append(CountOrderStatus(PAID_ORDER_STATUS, o))
            order_count.append(
                [
                    {
                        'type': 'text',
                        'value': o['date']
                    },
                    {
                        'type': 'text',
                        'value': CountOrderStatus(REQUEST_ORDER_STATUS, o)
                    },
                    {
                        'type':'text',
                        'value': CountOrderStatus(PAID_ORDER_STATUS, o)
                    },
                    {
                        'type':'text',
                        'value': CountOrderStatus(SCHEDULED_ORDER_STATUS, o)
                    },
                    {
                        'type':'text',
                        'value': CountOrderStatus(DONE_ORDER_STATUS, o)
                    },
                    {
                        'type':'price',
                        'value': o.get('item_price', 0)/100.0
                    }
                ]
            )

        data = {
            'title': '订单统计',
            'page': page + 1, # 当前页数
            'count': record_count, # 表格数据总条数
            'limit': PAGE_SIZE, # 数据一页的最大条数
            'thead': ['日期', '请求订单', '支付订单', '调度订单', '完成订单', '销售额'],
            'tdatas':  order_count,
            'series': [
                {
                    'name': '支付单量',
                    'type': 'line',
                    'data': list(reversed(paid_order_count)),
                    'feature': {
                        'max': False, # 自动计算最大值
                        'min': False, # 自动计算最小值
                        'avg': False # 自动计算平均值
                    }
                }
            ],
            'legend': ['Ding Dan'], # 图例文字
            'xAxis': list(reversed(order_date)), # 横坐标轴文字，显示年份20个放不下,显示月-日可以
            'areas': {
                'full': json.dumps(areas_with_schools),
                'choosed': json.dumps(
                    {
                        'area': region,
                        'province': province,
                        'city': city,
                        'campus': school_name
                    }
                )
            }
        }

        raise gen.Return(data)
