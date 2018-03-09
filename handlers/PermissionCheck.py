#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


import functools
from errors import PermissionDeny


def PermissionCheck(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        action = self.__class__.RequiredPrivilege
        privileges = self.current_user['privileges']
        if action in privileges:
            return method(self, *args, **kwargs)
        else:
            raise PermissionDeny()
    return wrapper
