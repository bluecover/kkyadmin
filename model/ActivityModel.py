#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'


from third_party.orm import Document
from third_party.orm import EmbeddedDocument
from third_party.orm import EmbeddedDocumentField
from third_party.orm import IntegerField
from third_party.orm import ListField
from third_party.orm import StringField
from third_party.orm import MobileField
from third_party.orm import LocationField
from third_party.orm.field import ObjectIdField
from tornado import gen
from bson import ObjectId
import time
import logging
import random
import settings

DEFAULT_ACTIVITY_RESULT = "ave"

class ActivityModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'activity'
    }
    user_id = ObjectIdField()
    created_time = IntegerField(required=True)
    activity_name = StringField(required=True)
    activity_result = StringField(required=True, default=DEFAULT_ACTIVITY_RESULT)
    activity_device = StringField(required=True)

    @classmethod
    @gen.coroutine
    def MarkDeviceIfNotJoinActivity(cls, device_token, activity_name, activity_result):
        condition = {
            "activity_device": device_token,
            "activity_name": activity_name
        }
        updater = {
            "$set": {
                "activity_device": device_token,
                "activity_name": activity_name,
                "created_time": int( time.time() * 1000)
            }
        }
        result = yield cls.update(condition, updater, upsert=True)
        if (result['updatedExisting'] is False) and ('upserted' in result):
            yield cls.update(condition, {"$set": {"activity_result": activity_result}})
        else:
            activity_record = yield cls.find_one(condition)
            activity_result = activity_record['activity_result']
        raise gen.Return( (True, activity_result) )

    @classmethod
    @gen.coroutine
    def GetDeviceActivityResult(cls, device_token, activity_name):
        condition = {
            "activity_device": device_token,
            "activity_name": activity_name
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def BindDeviceUserActivityResult(cls, device_token, user_id, activity_name):
        condition = {
            "activity_name": activity_name,
            "activity_device": device_token,
            "user_id": {"$exists": False}
        }
        updater = {
            "$set": {
                "user_id": user_id
            }
        }
        result = yield cls.update(condition, updater)
        if (result['ok'] == 1) and result['updatedExisting'] and (result['nModified'] > 0):
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @classmethod
    @gen.coroutine
    def GetUserActivity(cls, user_id, activity_name):
        condition = {
            "user_id": user_id,
            "activity_name": activity_name
        }
        activity = yield cls.find_one(condition)
        raise gen.Return(activity)
