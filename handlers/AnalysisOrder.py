#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/21/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class AnalysisOrder(RequestHandler):
    RequiredPrivilege = 'AnalysisRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '统计',
                'submenu': '订单统计',
                'content_src': '/analysis?method=simple&type=order',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id']
            }
        }
        self.render('index.html', data=data)
