#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from RequestHandler import RequestHandler
import settings


class Logout(RequestHandler):
    def get(self):
        if self.current_user:
            self.session.delete(settings.redis.USER_KEY)
            self.current_user = None
        self.redirect('/login')
