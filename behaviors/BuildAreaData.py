#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from Behavior import Behavior
from tornado import gen
import settings
from SchoolCache import SchoolCache
import time
import logging


class BuildAreaData(Behavior):
    @gen.coroutine
    def BuildAreas(self, user):
        limit_to_region = user['region']
        limit_to_province = user['province']
        limit_to_city = user['city']
        if not limit_to_region or limit_to_region == u'全部大区':
            limit_to_region = 'all'
        if not limit_to_province or limit_to_province == u'全部省份':
            limit_to_province = 'all'
        if not limit_to_city or limit_to_city == u'全部城市':
            limit_to_city = 'all'
        REGIONS = yield SchoolCache.Instance().GetRegions()
        areas = []
        for REGION in REGIONS:
            if limit_to_region != 'all' and REGION['name'] != limit_to_region:
                continue
            area_elem = {
                'n': REGION['name'],
                'd': []
            }

            for PROVINCE in REGION['province']:
                if limit_to_province != 'all' and PROVINCE['name'] != limit_to_province:
                    continue
                province_elem = {
                    'n': PROVINCE['name'],
                    'd': []
                }
                for CITY in PROVINCE['city']:
                    if limit_to_city != 'all' and CITY['name'] != limit_to_city:
                        continue
                    city_d = {
                        'n': CITY['name']
                    }
                    province_elem['d'].append(city_d)

                if user['city'] == u'全部城市':
                    final_province_d = [
                        {
                            'n': u'全部城市',
                            'd': [
                                {
                                    'n': u'全部校区'
                                }
                            ]
                        }
                    ] + province_elem['d']
                    province_elem['d'] = final_province_d

                area_elem['d'].append(province_elem)


            if user['province'] == u'全部省份':
                final_area_d = [
                    {
                        'n': u'全部省份',
                        'd': [
                            {
                                'n': u'全部城市',
                                'd': [
                                    {
                                        'n': u'全部校区'
                                    }
                                ]
                            }
                        ]
                    }
                ] + area_elem['d']
                area_elem['d'] = final_area_d

            areas.append(area_elem)


        if user['region'] == u'全部大区':
            all_area = {
                'n': u'全部大区',
                'd': [
                    {
                        'n': u'全部省份',
                        'd': [
                            {
                                'n': u'全部城市',
                                'd': [
                                    {
                                        'n': u'全部校区'
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
            final_areas = [all_area]
            final_areas.extend(areas)
        else:
            final_areas = areas

        raise gen.Return(final_areas)


    @gen.coroutine
    def BuildAreasWithSchools(self, user):
        start_time = time.time()

        areas = yield self.BuildAreas(user)
        # Attach schools!
        for area in areas:
            region_name = area['n']
            if region_name == u'全部大区':
                continue
            for province in area['d']:
                province_name = province['n']
                if province_name == u'全部省份':
                    continue
                for city in province['d']:
                    city_name = city['n']
                    if city_name == u'全部城市':
                        continue
                    city_d = []
                    if user['school_name'] == u'全部校区':
                        city_d.append( {'n': u'全部校区'} )
                    schools_of_city = yield SchoolCache.Instance().GetSchools(
                        region_name,
                        province_name,
                        city_name
                    )
                    for school in schools_of_city:
                        if user['school_name'] == u'全部校区' or user['school_id'] == school['_id']:
                            city_d.append(
                                {
                                    'n': school['name']
                                }
                            )
                    city['d'] = city_d

        duration = time.time() - start_time
        logging.info('[TIME] BuildAreasWithSchools: ' + str(duration))

        raise gen.Return(areas)


    @gen.coroutine
    def FindSchoolOfOrder(self, order):
        shop = yield self.shop_model.GetShopFromId(order['shop_id'])
        school = yield self.school_model.GetSchoolFromId(shop['school_district'])
        raise gen.Return(school)
