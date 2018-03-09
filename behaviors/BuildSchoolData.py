#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from Behavior import Behavior
from tornado import gen
from BuildAreaData import BuildAreaData
import json


class BuildSchoolData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        area_full = yield BuildAreaData().BuildAreas(kw['user'])
        data = {
            'area_full': json.dumps(area_full),
            'extra_btns': [
                {
                    'text': u'添加校区',
                    'href': '/campus_add'
                }
            ],
            'table_src': 'campus_list'
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

        PAGE_SIZE = 20
        page = kw['page'] - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE
        schools, schools_count = yield self.school_model.GetSchoolsAndCountFromArea(
            skip,
            limit,
            region=region,
            province=province,
            city=city,
        )

        datas = []
        for school in schools:
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': school.get('region', '')
                    },
                    {
                        'type': 'text',
                        'value': school.get('province', '')
                    },
                    {
                        'type': 'text',
                        'value': school.get('city', '')
                    },
                    {
                        'type': 'text',
                        'value':school['name']
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/campus_detail?id=%s")' % str(school['_id'])
                    }
                ]
            )

        data = {
            'thead': [u'大区', u'省份', u'城市', u'校区', u'操作'],
            'datas': datas,
            'count': schools_count
        }
        raise gen.Return(data)

    @gen.coroutine
    def BuildSchoolDetail(self, school_id):
        school = yield self.school_model.GetSchoolFromId(school_id)
        campus = {
            '_id': school['_id'],
            'area': school.get('region', ''),
            'province': school.get('province', ''),
            'city': school.get('city', ''),
            'campus': school.get('name', ''),
            'note': school.get('note', ''),
            'position': school.get('location', [0,0])
        }
        raise gen.Return(campus)
