#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 tinyproxy <tinyproxy@gmail.com>
#

""""""

from third_party.orm import Document
from third_party.orm import IntegerField
from third_party.orm import StringField
from third_party.orm.field import ObjectIdField
from tornado import gen
import time
import logging
import settings
import datetime

class UserShareModel(Document):
    meta = {'db': settings.mongodb.SHARK_DB, 'collection': 'user_share'}
    user_id = ObjectIdField(required=True)
    created_time = IntegerField(required=True)
    share_type = StringField(required=True)
    created_date_time = IntegerField(required=True)

    @classmethod
    @gen.coroutine
    def CreateUserShare(cls, user_id, share_type):
        now = datetime.datetime.now()
        timestamp = int(time.mktime(now.timetuple())* 1000)
        today = datetime.datetime(now.year, now.month, now.day)
        created_date_time = int(time.mktime(today.timetuple()) * 1000)
        data = {
            "user_id": user_id,
            "share_type": share_type,
            "created_time": timestamp,
            "created_date_time": created_date_time
        }
        share_id = cls.insert(data)
        raise gen.Return(share_id)
