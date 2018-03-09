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


ORDER_REFUND_REASONS = [
    'do_not_want',
    'user_info_error',
    'school_location_error',
    'dispatch_not_in_time',
    'dispatch_error'
]


class OrderRefundModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'order_refund'
    }


    order_id = ObjectIdField()
    created_time = IntegerField(required=True)
    reason = StringField(required=True, candidate=ORDER_REFUND_REASONS)
    detail = StringField()

    @classmethod
    def CandidateReasons(cls):
        return ORDER_REFUND_REASONS

    @classmethod
    @gen.coroutine
    def UpdateRecord(cls, order_id, reason, detail=''):
        condition = {
            'order_id': order_id
        }
        updater = {
            '$set': {
                'created_time': int(time.time() * 1000),
                'reason': reason,
                'detail': detail
            }
        }
        result = yield cls.update(condition, updater, upsert=True)
        raise gen.Return(result)


    @classmethod
    @gen.coroutine
    def GetRecord(cls, order_id):
        condition = {
            'order_id': order_id
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)
