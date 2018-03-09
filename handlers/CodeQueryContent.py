#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2015 Enjoy Online Ltd.
# 2015-03-30 22:22

__author__ = 'tinyproxy'

import logging
from tornado import gen
from RequestHandler import RequestHandler
from behaviors import CodeQuery

class CodeQueryContent(RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            "flag": "ok",
            "message": "",
            "code": "",
            "mobile": ""
        }
        self.render('helpdesk_authcode.html', data=data)

    @gen.coroutine
    def post(self, *args, **kwargs):
        code_type = self.get_argument('type', '')
        mobile = self.get_argument('mobile', '')
        if code_type in ['courier', 'user']:
            code = yield CodeQuery().Action(code_type, mobile)
            if code:
                data = {
                    "flag": "ok",
                    "message": "",
                    "code": code,
                    "mobile": mobile
                }
                logging.debug(data)
                self.render('helpdesk_authcode.html', data=data)
            else:
                data = {
                    "flag": "ok",
                    "message": "用户没有点击发送短信或已输入验证码",
                    "code": None,
                    "mobile": mobile
                }
                logging.debug(data)
                self.render('helpdesk_authcode.html', data=data)
        else:
            data = {
                'code': 10086,
                'flag': 'error',
                'message': 'invalid code type, please notify administor'
            }
            self.render('global_error.html', data=data)
