#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from third_party.orm import Document
from third_party.orm import ObjectIdField
from third_party.orm import StringField
from third_party.orm import IntegerField
import settings
from tornado import gen
import time


EXPEND_STATUS = [
    'unprocessed',
    'processed',
    'freezed'
]


class ExpendModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'expend'
    }

    withdraw_id = ObjectIdField(required=True)
    withdraw_amount = IntegerField(required=True)
    fine_amount = IntegerField(required=True)
    real_amount = IntegerField(required=True)
    status = StringField(required=True, candidate=EXPEND_STATUS, default='unprocessed')
    created_time = IntegerField(required=True)
    courier_id = ObjectIdField(required=True)
    school_id = ObjectIdField()
    courier_name = StringField()

    @classmethod
    @gen.coroutine
    def CreateExpendRecord(cls, courier_id, courier_name, withdraw_id, withdraw_amount,
                           fine_amount, expend_amount, school_id, status):
        data = {
            'courier_id': courier_id,
            'courier_name': courier_name,
            'withdraw_id': withdraw_id,
            'withdraw_amount': withdraw_amount,
            'fine_amount': fine_amount,
            'real_amount': expend_amount,
            'created_time': int(time.time() * 1000),
            'status': status
        }
        if school_id:
            data['school_id'] = school_id
        result = yield cls.insert(data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNew(cls, data):
        result = yield cls.insert(data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetExpendFromId(cls, id_to_find):
        condition = {'_id': id_to_find}
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetExpendsAndCountFromCourierId(cls, courier_id, skip=None, limit=None):
        condition = {
            'courier_id': courier_id
        }
        sort_condition = [
            ('created_time', -1)
        ]
        query = cls.find(condition)
        count = yield query.count()
        if skip is not None and limit is not None:
            docs = yield query.sort(sort_condition).skip(skip).limit(limit).to_list(None)
        else:
            docs = yield query.sort(sort_condition).to_list(None)
        result = (docs, count)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetProcessed(cls, expend_id):
        condition = {
            '_id': expend_id
        }
        updater = {
            '$set': { 'status': 'processed' }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)
