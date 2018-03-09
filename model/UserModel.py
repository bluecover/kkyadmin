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
from tornado import gen
from bson import ObjectId
import time
import logging
import settings

AREA_LEVELS = [
    'country',
    'region',
    'province',
    'city',
    'school'
]

class DeviceTokenModel(EmbeddedDocument):
    android = StringField()
    ios = StringField()

class UserModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'user'
    }

    mobile = MobileField(required=True)
    name = StringField()
    address = StringField()
    location = LocationField()
    created_time = IntegerField()

    area_level = StringField(candidate=AREA_LEVELS)
    area_name = StringField()
    device_token = EmbeddedDocumentField(DeviceTokenModel)

    @classmethod
    @gen.coroutine
    def GetUserFromId(cls, user_id):
        if isinstance(user_id, ObjectId) is False:
            user_id = ObjectId(user_id)
        result = yield cls.find_one({'_id': user_id})
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewIfNotExists(cls, mobile):
        user = yield cls.find_one({'mobile': mobile})
        if user:
            raise gen.Return(user['_id'])
        else:
            now = int(time.time()*1000)
            user_data = {
                'mobile': mobile,
                'created_time': now
            }
            result = yield cls.insert(user_data)
            raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetUserFromMobile(cls, mobile):
        condition = {"mobile": mobile}
        user = yield cls.find_one(condition)
        raise gen.Return(user)

    @classmethod
    @gen.coroutine
    def UpdateDeviceToken(cls, user_id, device_type, device_token):
        condition = {"_id": user_id}
        setter = {
            "$set": {
                "device_token": {
                    device_type: device_token
                }
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)
