#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/26/15'


from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
from third_party.orm import Document
from tornado import gen
import settings


STATUS_CANDIDATES = [
    'on',
    'off',
    'deleted'
]


class ItemRepoModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'item_repo'
    }

    category = StringField(required=True)
    name = StringField(required=True)
    price = IntegerField(required=True)
    priority = IntegerField(required=True, default=0)
    created_time = IntegerField(required=True)
    status = StringField(required=True, candidate=STATUS_CANDIDATES)
    number = IntegerField(required=True, unique=True)
    image_id = ObjectIdField()
    description = StringField()
    note = StringField()
    brand = StringField()
    special_price = IntegerField()
    limit = IntegerField()

    @classmethod
    @gen.coroutine
    def GetItemFromId(cls, item_id):
        condition = {
            '_id': item_id
        }
        item = yield cls.find_one(condition)
        raise gen.Return(item)

    @classmethod
    @gen.coroutine
    def UpdateItem(cls, item_id, item_data):
        condition = {
            '_id': item_id
        }
        updater = {
            '$set': item_data
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def InsertItem(cls, item_data):
        result = yield cls.insert(item_data)
        raise gen.Return(result)
