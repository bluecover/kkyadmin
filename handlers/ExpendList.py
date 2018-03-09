#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class ExpendList(RequestHandler):
    RequiredPrivilege = 'ExpendRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '财务',
                'submenu': '支出管理',
                'content_src': '/table?type=expenses_list',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id'],
            }
        }
        self.render('index.html', data=data)
