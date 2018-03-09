#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/12/15'


from Behavior import Behavior
from tornado import gen
import json
from BuildAreaData import BuildAreaData


class BuildBuildingData(Behavior):
    @gen.coroutine
    def BuildBuildingsOfArea(self, user, region=None, province=None, city=None, school=None):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(user)
        choosed = {
            'region': region,
            'province': province,
            'city': city,
            'school': school
        }
        if not choosed['school']:
            choosed = self._GetFirstSchool(areas_with_schools)

        school = yield self.school_model.GetSchoolFromName(choosed['school'])
        buildings = yield self.building_model.GetSchoolBuildings(school['_id'])
        data = {
            'building_dispatch': True if 'building' in school.get('dispatch_strategy',[]) else False,
            'school_id': school['_id'],
            'buildings': [
                {
                    'name': b['name'],
                    'arg_name': b['_id']
                } for b in buildings
            ],
            'areas': {
                'full': json.dumps(areas_with_schools),
                'choosed': json.dumps(
                    {
                        'area': choosed.get('region', ''),
                        'province': choosed.get('province', ''),
                        'city': choosed.get('city', ''),
                        'campus': choosed.get('school', '')
                    }
                )
            }
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildBuildingCouriersOfSchool(self, school_id):
        school = yield self.school_model.GetSchoolFromId(school_id)
        buildings = yield self.building_model.GetSchoolBuildings(school_id)
        couriers_of_school = yield self.courier_model.GetCouriersFromDistrictId(school_id)
        building_couriers_data = [
            {
                'name': b['name'],
                'arg_name': b['_id'],
                'couriers': [
                    {
                        'name': c['name'],
                        'arg_name': c['_id'],
                        'on': True if 'delivery_buildings' in c and b['_id'] in c['delivery_buildings'] else False
                    } for c in couriers_of_school
                ]
            } for b in buildings
        ]
        data = {
            'school_name': school['name'],
            'school_id': school['_id'],
            'building_couriers': building_couriers_data
        }
        raise gen.Return(data)


    def _GetFirstSchool(self, areas):
        first = {}
        for area in areas:
            region_name = area['n']
            if region_name == u'全部大区':
                continue
            first['region'] = region_name
            for province in area['d']:
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
