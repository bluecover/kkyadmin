#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/27/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildAreaData
from behaviors import BuildShopData
import json
import time
from bson import ObjectId


class ShopCreate(RequestHandler):
    RequiredPrivilege = 'ShopCreate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        areas_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        data = {
            'areas': {
                'full': json.dumps(areas_full)
            },
            'shop_add': True
        }
        self.render('detail_page_shop_edit.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        region = self.get_argument('area')
        province = self.get_argument('province')
        city = self.get_argument('city')
        campus = self.get_argument('campus')

        areas_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        data = {
            'flag': 'ok',
            'message': u'',
            'areas': {
                'full': json.dumps(areas_full)
            }
        }

        if u'全部' in region or u'全部' in province or u'全部' in city or u'全部' in campus:
            data['flag'] = 'error'
            data['message'] = u'添加店铺失败：未选择校区'
            self.render('detail_page_shop_edit.html', data=data)
            raise gen.Return(None)

        shop_data = yield BuildShopData().BuildShopFromRequest(self)
        shop_data['created_time'] = int(time.time()*1000)
        shop_data['image_id'] = self.GetShopImageId(shop_data['type'])

        school = yield self.school_model.GetSchoolFromName(campus)
        available_couriers = yield self.courier_model.GetCouriersFromDistrictId(school['_id'])
        if not available_couriers:
            shop_data['status'] = 'closed'

        result = yield self.shop_model.insert(shop_data)
        if result:
            self.redirect('/shop_detail?id=%s' % result)
        else:
            data['flag'] = 'error'
            data['message'] = u'添加店铺失败'
            self.render('detail_page_shop_edit.html', data=data)


    def GetShopImageId(self, type):
        return {
            'cvs':  ObjectId('550140ac778d1715b9420dfd'),
            'restaurant': ObjectId('5539b77e45c7f54b848dc97d'),
            'fruit': ObjectId('5539b7a130cb4abb0aaddebc'),
            'canteen': ObjectId('5539b77e45c7f54b848dc97d'),
            'drink': ObjectId('5539b7bff64648af49c971f7'),
            'express': ObjectId('5539b7dd16920b048c028eb9'),
            'laundry': ObjectId('5539b837d70c1334cb1f811f'),
            'cigarette': ObjectId('5539b5760ca0ba3b6dcc6a1a')
        }.get(type, ObjectId('550140ac778d1715b9420dfd'))
