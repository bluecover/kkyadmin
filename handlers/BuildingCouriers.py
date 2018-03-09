#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/12/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from errors import PermissionDeny
from behaviors import BuildBuildingData
from bson import ObjectId


class BuildingCouriers(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'BuildingRead' in self.current_user['privileges']:
            raise PermissionDeny()

        school_id = ObjectId(self.get_argument('school_id'))

        data = yield BuildBuildingData().BuildBuildingCouriersOfSchool(school_id)
        self.render('building_couriers.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'BuildingUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        school_id = ObjectId(self.get_argument('school_id'))
        buildings = yield self.building_model.GetSchoolBuildings(school_id)
        couriers = yield self.courier_model.GetCouriersFromDistrictId(school_id)
        for c in couriers:
            courier_buildings = []
            for b in buildings:
                arg_key = str(b['_id']) + '_' + str(c['_id'])
                if arg_key in self.request.arguments:
                    courier_buildings.append(b['_id'])
            yield self.courier_model.UpdateDeliveryBuildings(c['_id'], courier_buildings)

        school = yield self.school_model.GetSchoolFromId(school_id)
        data = yield BuildBuildingData().BuildBuildingCouriersOfSchool(school_id)
        self.render('building_couriers.html', data=data)
