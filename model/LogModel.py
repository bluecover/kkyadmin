#!/usr/bin/env python
# coding: utf-8
__author__ = 'wzy'
__date__ = '2015-06-15 17:10'


from third_party.orm import Document
from third_party.orm import ObjectIdField
from third_party.orm import IntegerField
from third_party.orm import StringField
from third_party.orm import GenericDictField
from tornado import gen
import time
import settings

class LogModel(Document):
    meta = {
        "db": settings.mongodb.CONSOLE_DB,
        "collection": "log"
    }

    # console user id
    user_id = ObjectIdField(required=True)
    action = StringField(required=True)
    created_time = IntegerField(required=True)
    status = IntegerField(required=True)
    ip = StringField(required=True)
    arguments = GenericDictField()

    @classmethod
    @gen.coroutine
    def NewLog(cls, user_id, action, status, ip, arguments):
        data = {
            'user_id': user_id,
            'action': action,
            'created_time': int(time.time()*1000),
            'status': status,
            'ip': ip,
            'arguments': arguments
        }
        log_id = yield cls.insert(data)
        raise gen.Return(log_id)
