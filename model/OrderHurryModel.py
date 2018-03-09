#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '6/2/15'


from third_party.orm import Document
from third_party.orm.field import StringField
from third_party.orm.field import ObjectIdField
from third_party.orm.field import IntegerField
import settings
from tornado import gen
import time


ORDER_HURRY_REASONS = [
    'no_available_courier',
    'courier_do_not_send',
    'courier_lose_contact',
    'already_delivered',
    'other'
]


class OrderHurryModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'order_hurry'
    }


    order_id = ObjectIdField()
    created_time = IntegerField(required=True)
    reason = StringField(required=True, candidate=ORDER_HURRY_REASONS)
    detail = StringField()


    @classmethod
    def CandidateReasons(cls):
        return ORDER_HURRY_REASONS


    @classmethod
    @gen.coroutine
    def CreateRecord(cls, order_id, reason, detail=''):
        data = {
            'order_id': order_id,
            'created_time': int(time.time() * 1000),
            'reason': reason,
            'detail': detail
        }
        result = yield cls.insert(data)
        raise gen.Return(result)


    @classmethod
    @gen.coroutine
    def GetRecords(cls, order_id):
        condition = {
            'order_id': order_id
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)
