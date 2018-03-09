#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck


class CategoryList(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('shop_id'))
        # skip = int(self.get_argument('skip', 0))
        # limit = int(self.get_argument('limit', 10))
        categories = yield self.category_model.GetCategoriesByShopId(shop_id)
        data = {
            'categories': categories
        }
        self.render(data)
