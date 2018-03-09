#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

""""""
from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
from third_party.orm.field import ListField
from third_party.orm import Document
from tornado import gen
import settings
import time


class ItemLimitModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'item_limit'
    }
    item_id = ObjectIdField(required=True)
    user_id = ObjectIdField(required=True)
    counter = IntegerField(required=True, default=int(0))
    updated_time = ListField(IntegerField(), required=True)

    @classmethod
    @gen.coroutine
    def UpdateUserItemCounter(cls, user_id, item_id, counter_inc):
        condition = {
            "user_id": user_id,
            "item_id": item_id
        }
        setter = {
            "$inc": {
                "counter": counter_inc
            },
            "$push": {
                "updated_time": int(time.time() * 1000)
            }
        }
        result = yield cls.update(condition, setter, upsert=True)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetUserItemLimit(cls, user_id, item_id):
        condition = {
            "user_id": user_id,
            "item_id": item_id
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)
