#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from behaviors import BuildShopData
from behaviors import BuildAreaData
import json
import decimal
from behaviors import ConvertText
from PermissionCheck import PermissionCheck


class ShopEdit(RequestHandler):
    RequiredPrivilege = 'ShopUpdate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('id'))
        shop = yield self.shop_model.GetShopFromId(shop_id)
        shop_data = yield BuildShopData().BuildShopDeatil(shop)
        areas_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        school_of_shop = yield self.school_model.GetSchoolFromId(shop['school_district'])
        if not school_of_shop:
            school_of_shop = {}
        data = {
            'shop': shop_data,
            'areas': {
                'full': json.dumps(areas_full),
                'choosed': json.dumps(
                    {
                        'area': school_of_shop.get('region', ''),
                        'province': school_of_shop.get('province', ''),
                        'city': school_of_shop.get('city', ''),
                        'campus': school_of_shop.get('name', '')
                    }
                )
            },
            'shop_add': False
        }
        self.render('detail_page_shop_edit.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('id'))
        shop_data = yield BuildShopData().BuildShopFromRequest(self)

        if shop_data['status'] == 'open':
            shop = yield self.shop_model.GetShopFromId(shop_id)
            school = yield self.school_model.GetSchoolFromId(shop['school_district'])
            available_couriers = yield self.courier_model.GetCouriersFromDistrictId(school['_id'])
            if not available_couriers:
                del shop_data['status']
                shop = yield self.shop_model.GetShopFromId(shop_id)
                shop_data = yield BuildShopData().BuildShopDeatil(shop)
                areas_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
                school_of_shop = yield self.school_model.GetSchoolFromId(shop['school_district'])
                if not school_of_shop:
                    school_of_shop = {}
                data = {
                    'shop': shop_data,
                    'areas': {
                        'full': json.dumps(areas_full),
                        'choosed': json.dumps(
                            {
                                'area': school_of_shop.get('region', ''),
                                'province': school_of_shop.get('province', ''),
                                'city': school_of_shop.get('city', ''),
                                'campus': school_of_shop.get('name', '')
                            }
                        )
                    }
                }
                data['flag'] = 'error'
                data['message'] = '没有工作的速递员，不能营业'
                self.render('detail_page_shop_edit.html', data=data)
                raise gen.Return(None)

        result = yield self.shop_model.UpdateShop(
            shop_id,
            shop_data
        )
        success = result['updatedExisting'] and result['ok'] == 1

        if success:
            self.redirect('/shop_detail?id=%s' % shop_id)
        else:
            shop = yield self.shop_model.GetShopFromId(shop_id)
            shop_data = yield BuildShopData().BuildShopDeatil(shop)
            areas_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
            school_of_shop = yield self.school_model.GetSchoolFromId(shop['school_district'])
            if not school_of_shop:
                school_of_shop = {}
            data = {
                'shop': shop_data,
                'areas': {
                    'full': json.dumps(areas_full),
                    'choosed': json.dumps(
                        {
                            'area': school_of_shop.get('region', ''),
                            'province': school_of_shop.get('province', ''),
                            'city': school_of_shop.get('city', ''),
                            'campus': school_of_shop.get('name', '')
                        }
                    )
                }
            }
            data['flag'] = 'error'
            data['message'] = '修改学校资料失败'
            self.render('detail_page_shop_edit.html', data=data)
