#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2015 Enjoy Online Ltd.
# 2015-03-30 22:19

__author__ = 'tinyproxy'

import logging
from tornado import gen
from RequestHandler import RequestHandler


class CodeQuery(RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            "system": {
                "menu": "客户服务",
                "submenu":"验证码查询",
                "content_src":"/helpdesk_authcode_content",
            },
            "user": {
                "name": self.current_user['name'],
                "_id": self.current_user['_id']
            }
        }
        self.render('index.html', data=data)

