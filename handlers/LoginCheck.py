#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/8/2015'


import functools


def LoginCheck(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.redirect('/login')
        else:
            return method(self, *args, **kwargs)
    return wrapper
