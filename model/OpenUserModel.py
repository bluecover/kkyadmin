#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2/2/15'

from third_party.orm import Document
from third_party.orm import EmbeddedDocument
from third_party.orm import EmbeddedDocumentField
from third_party.orm import IntegerField
from third_party.orm import StringField
from third_party.orm import MobileField
from third_party.orm import ObjectIdField
from third_party.orm import ListField
from third_party.orm import FloatField
from third_party.orm import LocationField
from tornado import gen
from bson import ObjectId
import time
import math
import random
import string
import logging
from third_party.orm.error import UniqueError
from errors import DuplicateError
import settings

OPEN_USER_STATUS_CANDIDATES = [
    "verifying",
    "verified"
]

class OpenUserModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'open_user'
    }
    name = StringField(required=True, unique=True)
    callback_url = StringField(required=True)
    secret = StringField(required=True)
    created_time = IntegerField(required=True)
    status = StringField(required=True, candidate=OPEN_USER_STATUS_CANDIDATES, default="verified")

    @classmethod
    @gen.coroutine
    def CreateNewOpenUser(cls, name, callback_url):
        secret = ''.join([random.choice(string.letters+string.digits) for _ in range(32)])
        data = {
            'name': name,
            'callback_url': callback_url,
            'secret': secret,
            'created_time': int(time.time() * 1000),
            'status': 'verified'
        }
        try:
            open_user_id = yield cls.insert(data)
            raise gen.Return(open_user_id)
        except UniqueError, e:
            value = ""
            if e.field == "name":
                value = name
            raise DuplicateError("'%s'"%e.field, value)
            pass

    @classmethod
    @gen.coroutine
    def GetOpenUserFromId(cls, uid):
        condition = {"_id": uid}
        user = yield cls.find_one(condition)
        raise gen.Return(user)

    @classmethod
    @gen.coroutine
    def CheckIdAndSecret(cls, app_id, app_secret):
        condition = {
            "_id": ObjectId(app_id),
            "secret": app_secret
        }
        user = yield cls.find_one(condition)
        raise gen.Return(user)
