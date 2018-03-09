#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildShopData
import logging


class ShopDetail(RequestHandler):
    RequiredPrivilege = 'ShopRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('id'))
        shop = yield self.shop_model.GetShopFromId(shop_id)
        if shop['school_name'] == 'kkyzh' and not 'sa' in self.current_user['roles']:
            raise gen.Return(None)
        shop_data = yield BuildShopData().BuildShopDeatil(shop)
        data = {
            'shop': shop_data
        }
        self.render('detail_page_shop.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        print self.request.arguments
        shop_id = ObjectId(self.get_argument('id'))
        condition = {
            '_id': shop_id
        }
        result = yield self.shop_model.remove(condition)
        logging.critical('ShopDelete: id[%s], user[%s]' % (shop_id, self.current_user['name']))
        self.redirect('/table?type=shop_list')
