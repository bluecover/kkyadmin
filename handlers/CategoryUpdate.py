#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck


class CategoryUpdate(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        category_id = ObjectId(self.get_argument('category_id'))
        new_values = {}

        name = self.get_argument('name', None)
        if name:
            new_values['name'] = name.encode('utf8')

        priority = self.get_argument('priority', None)
        if priority:
            new_values['priority'] = int(priority)

        result = yield self.category_model.UpdateCategory(category_id, **new_values)
        data = {}
        self.render(data)
