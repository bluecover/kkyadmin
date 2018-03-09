#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'


from third_party.orm import Document
from third_party.orm import EmbeddedDocument
from third_party.orm.field import MobileField
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
from third_party.orm.field import EmbeddedDocumentField
from third_party.orm.field import LocationField
from third_party.orm.field import ObjectIdField
from third_party.orm.field import ListField
from bson import ObjectId
import time
import logging
import settings
from tornado import gen


class ItemInOrderModel(EmbeddedDocument):
    _id = ObjectIdField(required=True)
    num = IntegerField(required=True)
    price = IntegerField(required=True)
    name = StringField(required=True)

class ReceivingModel(EmbeddedDocument):
    name = StringField(required=True, min_length=1, max_length=32)
    mobile = MobileField(required=True)
    location = LocationField(required=True)
    address = StringField(required=True, min_length=1, max_length=512)


ORDER_STATUS_CANDIDATE = [
    'unpaid',
    'cancel',
    'paid',
    'sending',
    'uncomment',
    'done',
    'refunded'
]


class OrderModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'order'
    }

    user_id = ObjectIdField(required=True)
    shop_id = ObjectIdField(required=True)
    building_id = ObjectIdField()
    items = ListField(
        EmbeddedDocumentField(ItemInOrderModel),
        required=True
    )
    receiving = EmbeddedDocumentField(ReceivingModel, required=True)
    created_time = IntegerField(required=True)
    status = StringField(
        required=True,
        default='unpaid',
        candidate=ORDER_STATUS_CANDIDATE
    )
    pay_type = StringField(candidate=['alipay', 'wxpay'], required=True)

    total_price = IntegerField()
    items_price = IntegerField()
    delivery_price = IntegerField()
    discount_price = IntegerField()
    coupon_id = ObjectIdField()
    remark = StringField()
    pay_total = IntegerField()
    pay_id = ObjectIdField()
    paid_time = IntegerField()
    confirm_time = IntegerField()
    done_time = IntegerField()
    cancel_time = IntegerField()
    sending_time = IntegerField()
    comment_type = StringField(candidate=['good', 'bad'])
    comment = StringField()
    courier_id = ObjectIdField()
    courier_name = StringField()
    courier_mobile = MobileField()
    express_id = ObjectIdField() # wukong express id

    region = StringField()
    province = StringField()
    city = StringField()
    school = StringField()

    school_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def CreateNewOrder(cls, order):
        order_id = yield cls.insert(order)
        raise gen.Return(order_id)

    @classmethod
    @gen.coroutine
    def GetOrdersFromUserId(cls, user_id, skip, limit):
        condition = {
            'user_id': user_id
        }
        sort_condition = [
            ('created_time', -1)
        ]
        orders = yield cls.find(condition).sort(sort_condition).skip(skip).limit(limit).to_list(None)
        raise gen.Return(orders)

    @classmethod
    @gen.coroutine
    def GetOrderFromId(cls, order_id, status=None):
        condition = {
            '_id': order_id
        }
        if status:
            condition['status'] = status
        order = yield cls.find_one(condition)
        raise gen.Return(order)

    @classmethod
    @gen.coroutine
    def MarkOrderPaid(cls, order_id, pay_id):
        condition = {
            '_id': order_id,
            'status': 'unpaid'
        }
        updater = {
            '$set': {
                'pay_id': pay_id,
                'paid_time': int(time.time()*1000),
                'status': 'paid'
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetOrderConfirmed(cls, user_id, order_id):
        condition = {
            '_id': order_id,
            'status': {
                '$in': ['paid', 'sending']
            }
        }
        updater = {
            '$set': {
                'status': 'uncomment',
                'confirm_time': int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetOrderConfirmedFromExpressId(cls, express_id):
        condition = {
            "express_id": express_id
        }
        updater = {
            "$set": {
                "status": "uncomment",
                "confirm_time": int(time.time() * 1000)
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetOrderCanceled(cls, user_id, order_id):
        condition = {
            '_id': order_id,
            'status': 'unpaid'
        }
        updater = {
            '$set': {
                'status': 'cancel',
                'cancel_time': int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetOrderComment(cls, user_id, order_id, comment_type, comment):
        condition = {
            '_id': order_id,
            'status': 'uncomment'
        }
        updater = {
            '$set': {
                'status': 'done',
                'done_time': int(time.time()*1000),
                'comment_type': comment_type,
                'comment': comment
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetOrderExpressId(cls, order_id, express_id):
        if not isinstance(express_id, ObjectId):
            express_id = ObjectId(express_id)
        condition = {
            "_id": order_id,
        }
        updater = {
            "$set": {
                "express_id": express_id
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetOrderFromExpressId(cls, express_id):
        if not isinstance(express_id, ObjectId):
            express_id = ObjectId(express_id)
        condition = {
            "express_id": express_id
        }
        order = yield cls.find_one(condition)
        raise gen.Return(order)

    @classmethod
    @gen.coroutine
    def SetOrderStatusSendingFromExpressId(cls, express_id, courier_id, courier_name, courier_mobile):
        if express_id and not isinstance(express_id, ObjectId):
            express_id = ObjectId(express_id)
        if courier_id and not isinstance(courier_id, ObjectId):
            courier_id = ObjectId(courier_id)
        condition = {
            "express_id": express_id,
            "status": "paid"
        }
        updater = {
            "$set": {
                "status": "sending",
                "sending_time": int(time.time()*1000),
            }
        }
        if courier_name:
            updater["$set"]["courier_name"] = courier_name
        if courier_mobile:
            updater["$set"]["courier_mobile"] = courier_mobile
        if courier_id:
            updater["$set"]["courier_id"] = courier_id
        logging.debug(condition)
        logging.debug(updater)
        result = yield cls.update(condition, updater)
        logging.debug(result)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetUnconfirmedOrders(cls):
        condition = {
            'status': {
                '$in': ['sending']
            }
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)
