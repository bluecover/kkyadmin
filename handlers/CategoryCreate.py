#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck


class CategoryCreate(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('shop_id'))
        name = self.get_argument('name').encode('utf8')
        priority = int(self.get_argument('priority', 0))
        category_id = yield self.category_model.CreateNewCategory(
            shop_id,
            name,
            priority
        )
        data = {
            '_id': category_id
        }
        self.render(data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('shop_id'))
        name = self.get_argument('name').encode('utf8')
