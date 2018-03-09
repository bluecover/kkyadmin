#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2015 Enjoy Online Ltd.
# 2015-03-30 22:59

__author__ = 'tinyproxy'

import logging
from tornado import gen
from Behavior import Behavior


class CodeQuery(Behavior):
    __NAME_SAPCE__ = "__mobile__"
    @gen.coroutine
    def Action(self, code_type, mobile):
        key = self.__NAME_SAPCE__ + mobile
        code = ""
        logging.debug(code_type)
        logging.debug(self.shark_redis)
        if code_type == "user":
            code = yield gen.Task(self.shark_redis.get, key)
        elif code_type == "courier":
            code = yield gen.Task(self.wukong_redis.get, key)
        raise gen.Return(code)

