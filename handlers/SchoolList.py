#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class SchoolList(RequestHandler):
    RequiredPrivilege = 'SchoolRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '团队',
                'submenu': '校区管理',
                'content_src': '/table?type=campus_list',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id'],
            }
        }
        self.render('index.html', data=data)
