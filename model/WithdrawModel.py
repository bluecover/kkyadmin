#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'

from third_party.orm import Document
from third_party.orm import StringField
from third_party.orm import ObjectIdField
from third_party.orm import FloatField
from third_party.orm import IntegerField
from tornado import gen
import time
import logging
import settings

WITHDRAW_STATUS = [
    'unprocessed',
    'processed'
]


class WithdrawModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'withdraw'
    }
    courier_id = ObjectIdField(required=True)
    account_type = StringField(required=True)
    account = StringField(required=True)
    name = StringField(required=True)
    money = IntegerField(required=True)
    bank_name = StringField()
    bank_province_city = StringField()
    bank_city = StringField()
    bank_branch = StringField()
    status = StringField(required=True, candidate=WITHDRAW_STATUS, default='unprocessed')
    created_time = IntegerField(required=True)
    trade_no = StringField()
    school_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def GetCourierWithdraws(cls, courier_id, limit=50, skip=0):
        condition = {
            'courier_id': courier_id
        }
        sort_condition = [
            ('created_time', -1)
        ]
        withdraws = yield cls.find(condition).limit(limit).skip(skip).sort(sort_condition).to_list(None)
        raise gen.Return(withdraws)

    @classmethod
    @gen.coroutine
    def CreateWithdrawRecord(cls, school_id, courier_id, account_type, account, name, money,
                             bank_name=None, bank_province_city=None, bank_branch=None):
        data = {
            'school_id': school_id,
            'courier_id': courier_id,
            'account_type': account_type,
            'account': account,
            'name': name,
            'money': money,
            'bank_name': bank_name,
            'bank_province_city': bank_province_city,
            'bank_branch': bank_branch,
            'created_time': int(time.time()*1000)
        }
        withdraw_id = yield cls.insert(data)
        raise gen.Return(withdraw_id)

    @classmethod
    @gen.coroutine
    def GetWithdrawFromId(cls, withdraw_id):
        condition = {'_id': withdraw_id}
        withdraw = yield cls.find_one(condition)
        raise gen.Return(withdraw)

    @classmethod
    @gen.coroutine
    def MarkWithdrawProcessed(cls, withdraw_id, trade_no):
        condition = {
            '_id': withdraw_id,
            'status': 'unprocessed'
        }
        setter = {
            '$set': {
                'status': 'processed'
            }
        }
        if trade_no:
            setter['$set']['trade_no'] = trade_no
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def ListWithdraws(cls, courier_id, limit=20, skip=0):
        query_condition = {
            "courier_id": courier_id
        }
        sort_condition = [
            ('created_time', -1)
        ]
        withdraws = yield cls\
            .find(query_condition)\
            .sort(sort_condition)\
            .limit(limit)\
            .skip(skip)\
            .to_list(None)
        raise gen.Return(withdraws)
