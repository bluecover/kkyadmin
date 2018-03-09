#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck


class Dashboard(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'system': {
                'menu': '',
                'submenu': '',
                'content_src': '/dashboard_content',
            },
            'user': {
                'name': self.current_user['name'],
                '_id': self.current_user['_id'],
            }
        }
        self.render('index.html', data=data)
