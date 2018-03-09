#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/3/21'


from RequestHandler import RequestHandler
from tornado import gen
from behaviors import HashPassword


class Login(RequestHandler):
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {}
        self.render('login.html', data=data)

    @gen.coroutine
    def post(self, *args, **kwargs):
        uname = self.get_argument('username', '').encode('utf8')
        upass = self.get_argument('password', '').encode('utf8')
        upass_hash = HashPassword().Action(upass)
        user = yield self.console_user_model.CheckPassword(uname, upass_hash)
        if uname and upass and user:
            if user['status'] in ['locked']:
                data = {
                    'flag': 'error',
                    'message': '帐号已被锁定，无法登录'
                }
                self.render('login.html', data=data)
            else:
                yield self.Login(user)
                self.redirect('/dashboard')
        else:
            data = {
                'flag': 'error',
                'message': '用户名或密码错误'
            }
            self.render('login.html', data=data)
