#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '15-5-31'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from errors import PermissionDeny
from behaviors import BuildExpendData


class ExpendDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'ExpendRead' in self.current_user['privileges']:
            raise PermissionDeny()

        expend_id = ObjectId(self.get_argument('id'))
        data = yield BuildExpendData().BuildExpendDetail(expend_id)
        self.render('detail_page_expenses.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'ExpendUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        expend_id = ObjectId(self.get_argument('id'))
        process = self.get_argument('process', '')
        if process:
            result = yield self.expend_model.SetProcessed(expend_id)
        data = yield BuildExpendData().BuildExpendDetail(expend_id)
        data['flag'] = 'ok'
        data['message'] = '处理成功'
        self.render('detail_page_expenses.html', data=data)
