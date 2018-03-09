#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/12/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class Building(RequestHandler):
    RequiredPrivilege = 'BuildingRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '配送',
                'submenu': '楼栋管理',
                'content_src': '/building_content',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id']
            }
        }
        self.render('index.html', data=data)
