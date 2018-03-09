#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/30/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class CourierWorkhour(RequestHandler):
    RequiredPrivilege = 'ScheduleRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                        'menu': '配送',
                        'submenu': '速递员排班',
                        'content_src': '/courier_workhour_content',
                    },
                'user': {
                    'name': self.current_user['name'],
                    '_id': self.current_user['_id'],
                }
        }
        self.render('index.html', data=data)
