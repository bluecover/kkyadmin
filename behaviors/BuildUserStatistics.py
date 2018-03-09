#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/24/15'


from Behavior import Behavior
from tornado import gen
import json
from BuildAreaData import BuildAreaData


class BuildUserStatistics(Behavior):
    @gen.coroutine
    def BuildUserStatisticsOfRegion(self, user, region, province, city, school_name, page=1):
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
        query = self.user_statistics.find(condition)
        record_count = yield query.count()
        records = yield query.sort(sort_condition).limit(limit).skip(skip).to_list(None)

        dates = []
        counts = []
        series_counts = []
        for r in records:
            dates.append(r['date'][4:].encode('utf8'))
            series_counts.append(r['new_users'])
            counts.append(
                [
                    {
                        'type': 'text',
                        'value': r['date']
                    },
                    {
                        'type': 'text',
                        'value': r['new_users']
                    },
                    {
                        'type':'text',
                        'value': r['total_users']
                    }
                ]
            )

        data = {
            'title': '用户',
            'page': page + 1, # 当前页数
            'count': record_count, # 表格数据总条数
            'limit': PAGE_SIZE, # 数据一页的最大条数
            'thead': ['日期','新增用户','累计用户'],
            'tdatas':  counts,
            'series': [
                {
                    'name': '新增用户',
                    'type': 'line',
                    'data': list(reversed(series_counts)),
                    'feature': {
                        'max': False, # 自动计算最大值
                        'min': False, # 自动计算最小值
                        'avg': False # 自动计算平均值
                    }
                }
            ],
            'legend': ['Yong Hu'], # 图例文字
            'xAxis': list(reversed(dates)), # 横坐标轴文字，显示年份20个放不下,显示月-日可以
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
