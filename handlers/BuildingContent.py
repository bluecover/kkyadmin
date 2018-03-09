#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/12/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from behaviors import BuildBuildingData
from errors import PermissionDeny
from bson import ObjectId


class BuildingContent(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'BuildingRead' in self.current_user['privileges']:
            raise PermissionDeny()

        area = self.get_argument('area', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        campus = self.get_argument('campus', '')
        if campus == u'全部校区':
            campus = None

        data = yield BuildBuildingData().BuildBuildingsOfArea(
            self.current_user,
            area,
            province,
            city,
            campus
        )

        self.render('building.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'BuildingUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        school_id = ObjectId(self.get_argument('school_id'))
        building_dispatch = self.get_argument('building_dispatch', None)

        if building_dispatch:
            yield self.school_model.SetDispatchStrategy(school_id, 'building')
        else:
            yield self.school_model.DeleteDispatchStrategy(school_id, 'building')

        buildings = yield self.building_model.GetSchoolBuildings(school_id)
        deleted = []
        for b in buildings:
            arg_name = 'name_' + str(b['_id'])
            name = self.get_argument(arg_name, None)
            if not name:
                deleted.append(b['_id'])
                continue
            condition = { '_id': b['_id'] }
            setter = { '$set': {} }
            if name:
                setter['$set']['name'] = name
            result = yield self.building_model.update(condition, setter)

        yield self.building_model.remove(
            {
                '_id': { '$in': deleted }
            }
        )

        exist_building_name = []
        for k,v in self.request.arguments.items():
            if k.startswith('newnode_'):
                id = k[8:]
                name_key = 'name_newnode_' + id
                name = self.get_argument(name_key)
                exist_building = yield self.building_model.find_one(
                    {
                        'school_id': school_id,
                        'name': name
                    }
                )
                if exist_building:
                    exist_building_name.append(name)
                else:
                    result = yield self.building_model.insert(
                        {
                            'school_id': school_id,
                            'name': name
                        }
                    )

        school = yield self.school_model.GetSchoolFromId(school_id)
        data = yield BuildBuildingData().BuildBuildingsOfArea(
            self.current_user,
            school['region'],
            school['province'],
            school['city'],
            school['name']
        )

        if exist_building_name:
            data['flag'] = 'error'
            names = ''
            for name in exist_building_name:
                names += ' ' + name
            data['message'] = u'重复校区名：' + names

        self.render('building.html', data=data)
