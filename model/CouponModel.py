#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'

import datetime
from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
from third_party.orm import Document
from tornado import gen
import time
import settings
from bson import ObjectId

COUPON_CANDIDATES = [
    'red_packet',
    'egg_coupon'
]

COUPON_STATES = [
    'unused',
    'using',
    'used'
]

DEFAULT_COUPON_TTL = 604800000 # 1 week = 604800000 ms

class CouponModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'coupon'
    }

    name = StringField(required=True, default="红包")
    user_id = ObjectIdField(required=True)
    type = StringField(required=True, default='red_packet', candidate=COUPON_CANDIDATES)
    status = StringField(required=True, default='unused', candidate=COUPON_STATES)
    money = IntegerField(required=True)
    confine = IntegerField(required=True, default=0)
    created_time = IntegerField(required=True)
    description = StringField() # coupon description, if we need it

    effect_time = IntegerField(required=True, default=0)
    expiration_time = IntegerField(required=True, default=long(13572115200000)) # 2400/2/1, it means never expire for us

    @classmethod
    @gen.coroutine
    def GetCoupons(cls, user_id, coupon_type="red_packet", limit=20, skip=0):
        condition = {
            "user_id": user_id,
            "type": coupon_type,
        }
        sort_condition = [
            ('created_time', -1)
        ]
        coupons = yield cls.find(condition).limit(limit).skip(skip).sort(sort_condition).to_list(None)
        raise gen.Return(coupons)

    @classmethod
    @gen.coroutine
    def GetCouponFromId(cls, coupon_id):
        condition = {
            '_id': coupon_id
        }
        coupon = yield cls.find_one(condition)
        raise gen.Return(coupon)

    @classmethod
    @gen.coroutine
    def SetCouponStatus(cls, coupon_id, status):
        if not status in COUPON_STATES:
            raise gen.Return(None)
        condition = {
            '_id': coupon_id
        }
        updater = {
            '$set': {
                'status': status
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateActivityCoupon(cls, user_id, activity_name, money,
        effect_time=-1, expiration_time=-1, confine=0):
        if effect_time == -1:
            effect_time = int(time.time() * 1000)
        if expiration_time == -1:
            expiration_time = int(time.time() * 1000) + DEFAULT_COUPON_TTL
        data = {
            "user_id": user_id,
            "money": money,
            "created_time": int (time.time() * 1000),
            "description": activity_name,
            "effect_time": effect_time,
            "expiration_time": expiration_time,
            "confine": confine
        }
        result = yield cls.insert(data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreatePrizeCoupon(cls, user_id, money,
        effect_time=-1, expiration_time=-1, confine=0):
        now = int(time.time() * 1000)
        if effect_time == -1:
            effect_time = now
        if expiration_time == -1:
            current_date = datetime.datetime.now()
            tomorrow = datetime.datetime(current_date.year, current_date.month, current_date.day) + datetime.timedelta(days=1)
            expiration_time = now + int( (tomorrow - current_date).total_seconds() * 1000 )
        data = {
            "user_id": user_id,
            "money": money,
            "created_time": now,
            "description": "下单奖励",
            "effect_time": effect_time,
            "expiration_time":expiration_time,
            "confine": 0,
            "type": "egg_coupon"
        }
        coupon_id = yield cls.insert(data)
        raise gen.Return(coupon_id)


    @classmethod
    @gen.coroutine
    def CreateServiceCoupon(cls, user_id, description, money,
        effect_time=-1, expiration_time=-1, confine=0, name=''):
        now = int(time.time() * 1000)
        if effect_time == -1:
            effect_time = now
        if expiration_time == -1:
            current_date = datetime.datetime.now()
            tomorrow = datetime.datetime(current_date.year, current_date.month, current_date.day) + datetime.timedelta(days=1)
            expiration_time = now + int( (tomorrow - current_date).total_seconds() * 1000 )

        if not name:
            name = '补偿红包'

        data = {
            "user_id": ObjectId(user_id),
            "money": money,
            "created_time": now,
            "description": description,
            "effect_time": effect_time,
            "expiration_time": expiration_time,
            "confine": confine,
            "name": name
        }
        coupon_id = yield cls.insert(data)
        raise gen.Return(coupon_id)



