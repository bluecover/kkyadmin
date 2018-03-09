#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


from third_party.orm import Document
from third_party.orm import ObjectIdField
from third_party.orm import StringField
from third_party.orm import FloatField
from third_party.orm import IntegerField
from tornado import gen
import time
import datetime
import math
import logging
import settings


BILL_TYPES = [
# if we append bill type, please check tools/UpdateDailyIncome.py script
# we do not compute negative bill
    'task',
    'withdraw',
    'fine',
    'reward',
    'subtask',
    'order_fee'  # shipping fee
]


class BillModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'bill'
    }
    courier_id = ObjectIdField()
    task_id = ObjectIdField()
    withdraw_id = ObjectIdField()
    money = IntegerField(required=True)
    type = StringField(required=True, candidate=BILL_TYPES)
    created_time = IntegerField(required=True)
    subtask_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def CreateTaskBill(cls, courier_id, task):
        task_id = task['_id']
        money = task['money']  #? task payment?
        data = {
            'courier_id': courier_id,
            'task_id': task_id,
            'type': 'task',
            'money': money,
            'created_time': int(time.time()*1000)
        }
        bill_id = yield cls.insert(data)
        raise gen.Return(bill_id)

    @classmethod
    @gen.coroutine
    def CreateWithdrawBill(cls, courier_id, withdraw_id, money):
        money = 0 - math.fabs(money)
        data = {
            'courier_id': courier_id,
            'withdraw_id': withdraw_id,
            'money': money,
            'type': 'withdraw',
            'created_time': int(time.time()*1000)
        }
        bill_id = yield cls.insert(data)
        raise gen.Return(bill_id)

    @classmethod
    @gen.coroutine
    def ListTodayIncomeBill(cls, courier_id):
        now = datetime.datetime.now()
        today = datetime.datetime(now.year, now.month, now.day)
        _0 = datetime.datetime.fromtimestamp(0)
        today_time = int( (today - _0).total_seconds() * 1000 )
        condition = {
            "created_time": {
                "$gte": today_time
            },
            "type": 'order_fee',
            "courier_id": courier_id
        }
        bills = yield cls.find(condition).to_list(None)
        raise gen.Return(bills)

    @classmethod
    @gen.coroutine
    def ListBills(cls, courier_id, limit=20, skip=0):
        query_condition = {
            "courier_id": courier_id
        }
        sort_condition = [
            ('created_time', -1)
        ]
        bills = yield cls\
            .find(query_condition)\
            .sort(sort_condition)\
            .limit(limit)\
            .skip(skip)\
            .to_list(None)
        raise gen.Return(bills)

    @classmethod
    @gen.coroutine
    def CreateSubtaskBill(cls, courier_id, subtask_id, pay):
        data = {
            'courier_id': courier_id,
            'subtask_id': subtask_id,
            'type': 'subtask',
            'money': pay,
            'created_time': int(time.time()*1000)
        }
        bill_id = yield cls.insert(data)
        raise gen.Return(bill_id)

    @classmethod
    @gen.coroutine
    def CreateOrderFeeBill(cls, courier_id, subtask_id, money):
        data = {
            "courier_id": courier_id,
            "subtask_id": subtask_id,
            "money": money,
            "created_time": int(time.time() * 1000),
            "type": "order_fee"
        }
        bill_id = yield cls.insert(data)
        raise gen.Return(bill_id)

    @classmethod
    @gen.coroutine
    def CreateFineBill(cls, courier_id, withdraw_id, fine_amount):
        data = {
            "courier_id": courier_id,
            "withdraw_id": withdraw_id,
            "money": fine_amount,
            "created_time": int(time.time() * 1000),
            "type": "fine"
        }
        bill_id = yield cls.insert(data)
        raise gen.Return(bill_id)
