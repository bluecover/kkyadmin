#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/3/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
import logging


class ShopDelete(RequestHandler):
    RequiredPrivilege = 'ShopDelete'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('id'))
        condition = {
            '_id': shop_id
        }
        result = yield self.shop_model.remove(condition)
        logging.critical('ShopDelete: id[%s], user[%s]' % (shop_id, self.current_user['name']))
        self.redirect('/table?type=shop_list')
