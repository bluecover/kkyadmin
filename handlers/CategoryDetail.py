#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck


class CategoryDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        data = {}
        self.render(data)
