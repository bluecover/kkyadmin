#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from behaviors import BuildCourierData
from errors import PermissionDeny


class CourierDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'CourierRead' in self.current_user['privileges']:
            raise PermissionDeny()
        courier_id = ObjectId(self.get_argument('id'))
        courier = yield self.courier_model.GetCourierFromId(courier_id)
        data = yield BuildCourierData().BuildCourierDeatil(courier, self.current_user)
        self.render('detail_page_courier.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'CourierUpdate' in self.current_user['privileges']:
            raise PermissionDeny()
        courier_id = ObjectId(self.get_argument('id'))
        name = self.get_argument('name', None)
        school = self.get_argument('campus', None)
        mobile = self.get_argument('mobile', None)
        verify_result = self.get_argument('pass', None)
        lock_result = self.get_argument('lock', None)
        longitude = self.get_argument('lng', None)
        latitude = self.get_argument('lat', None)

        new_data = {}
        if name:
            new_data['name'] = name
        if mobile:
            new_data['mobile'] = mobile
        if verify_result == 'pass':
            new_data['status'] = 'verified'
        if verify_result == 'reject':
            new_data['status'] = 'failed'
        if lock_result == 'lock':
            new_data['status'] = 'locked'
        if lock_result == 'unlock':
            new_data['status'] = 'verified'
        if latitude and latitude:
            new_data['location'] = [float(longitude), float(latitude)]

        region = self.get_argument('area', None)
        province = self.get_argument('province', None)
        city = self.get_argument('city', None)
        school = self.get_argument('campus', None)

        if school:
            school = yield self.school_model.GetSchoolFromName(school)
            if school:
                new_data['district_id'] = school['_id']
                new_data['school'] = school['name']

        condition = {
            '_id': courier_id
        }
        updater = {
            '$set': new_data
        }

        result = yield self.courier_model.update(condition, updater)

        courier = yield self.courier_model.GetCourierFromId(courier_id)

        courier_school_id = courier.get('district_id')
        if courier_school_id:
            available_couriers = yield self.courier_model.GetCouriersFromDistrictId(courier_school_id)
            if not available_couriers:
                result = yield self.shop_model.update(
                    { 'school_district': courier_school_id },
                    { '$set': { 'status': 'closed' } },
                    multi=True
                )

        data = yield BuildCourierData().BuildCourierDeatil(courier, self.current_user)
        self.render('detail_page_courier.html', data=data)
