#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/26/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class OrderList(RequestHandler):
    RequiredPrivilege = 'OrderRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '运营',
                'submenu': '订单管理',
                'content_src': '/table?type=order_list',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id'],
            }
        }
        self.render('index.html', data=data)
