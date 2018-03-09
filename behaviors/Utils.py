#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/22/15'


from Behavior import Behavior
from tornado import gen


class Utils(Behavior):
    @gen.coroutine
    def BuildSchoolCondition(self, region, province, city, school, school_key=None):
        if region == u'全部大区':
            region = None
        if province == u'全部省份':
            province = None
        if city == u'全部城市':
            city = None
        if school == u'全部校区':
            school = None

        if not region and not province and not city and not school:
            school_condition = {}
        else:
            schools, _ = yield self.school_model.GetSchoolsAndCountFromArea(
                region=region,
                province=province,
                city=city,
                school=school
            )
            if school_key:
                school_condition = {
                    school_key: {
                        '$in': [s['_id'] for s in schools]
                    }
                }
            else:
                school_condition = {
                    'school_id': {
                        '$in': [s['_id'] for s in schools]
                    }
                }

        raise gen.Return(school_condition)


    def GetFirstSchoolInRegion(self, regions):
        first = {}
        for region in regions:
            region_name = region['n']
            if region_name == u'全部大区':
                continue
            first['region'] = region_name
            for province in region['d']:
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
