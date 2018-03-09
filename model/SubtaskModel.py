#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


from third_party.orm import Document
from third_party.orm import EmbeddedDocument
from third_party.orm import MobileField
from third_party.orm import IntegerField
from third_party.orm import StringField
from third_party.orm import EmbeddedDocumentField
from third_party.orm import LocationField
from third_party.orm import ObjectIdField
from third_party.orm import ListField
from tornado import gen
from bson import ObjectId
import time
import random
import string
import logging
import settings
if settings.base.APP_NAME == "CONSOLE":
    pass
elif settings.base.APP_NAME == "WUKONG":
    from settings.base import CONFIRM_CODE_LENGTH
elif settings.base.APP_NAME == "SHARK":
    pass
elif settings.base.APP_NAME == "":
    pass
else:
    pass


SUBTASK_STATUS = [
    'submitted',
    'waiting',
    'scheduled',  # Has been grouped to a task to do.
    'dispatched', # Has been dispatched to a courier.
    'preparing',
    'delivering',
    'confirmed',
    'done',
    'canceled',
    'lock_for_confirm'
]


class TargetModel(EmbeddedDocument):
    name = StringField(required=True, min_length=1, max_length=32)
    mobile = MobileField(required=True)
    location = LocationField(required=True)
    address = StringField(required=True, min_length=1, max_length=512)


class ItemInSubtaskModel(EmbeddedDocument):
    item_id = ObjectIdField(required=True)
    name = StringField(required=True)
    count = IntegerField(required=True)
    price = IntegerField(required=True)
    description = StringField()
    image_id = ObjectIdField(required=True)


class SubtaskModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'subtask'
    }
    target = EmbeddedDocumentField(TargetModel)
    status = StringField(required=True, default='submitted', candidate=SUBTASK_STATUS)
    items = ListField(EmbeddedDocumentField(ItemInSubtaskModel), required=True)
    owner_task = ObjectIdField()
    created_time = IntegerField(required=True)
    scheduled_time = IntegerField()
    dispatched_time = IntegerField()
    start_time = IntegerField()
    done_time = IntegerField()
    shop_id = ObjectIdField()
    shop_location = LocationField()
    confirm_code = StringField(required=True)
    pay = IntegerField(required=True, default=0)
    express_no = StringField(required=True)
    app_id = ObjectIdField(required=True)
    comment = StringField(required=True, default="")

    delivery_price = IntegerField()
    order_id = ObjectIdField()

    building_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def GetSubtaskFromExpressNo(cls, express_no):
        condition = {
            "express_no": express_no
        }
        subtask = yield cls.find_one(condition)
        raise gen.Return(subtask)

    @classmethod
    @gen.coroutine
    def GetCourierSubtask(cls, courier_id, subtask_id):
        if not isinstance(courier_id, ObjectId):
            courier_id = ObjectId(courier_id)
        if not isinstance(subtask_id, ObjectId):
            subtask_id = ObjectId(subtask_id)

        condition = {
            '_id': subtask_id,
            'courier_id': courier_id
        }
        task = yield cls.find_one(condition)
        raise gen.Return(task)

    @classmethod
    @gen.coroutine
    def GetSubtaskFromId(cls, subtask_id):
        if not isinstance(subtask_id, ObjectId):
            subtask_id = ObjectId(subtask_id)

        condition = {
            '_id': subtask_id,
        }
        task = yield cls.find_one(condition)
        raise gen.Return(task)

    @classmethod
    @gen.coroutine
    def CreateWaitingSubtask(cls, app_id, express_no, shop_id, shop_location, target, items, payment, delivery_price, comment,
                             building_id=None):
        confirm_code = ''.join([random.choice(string.digits) for _ in range(CONFIRM_CODE_LENGTH)])
        data = {
            "app_id": app_id,
            "shop_id": shop_id,
            "shop_location": shop_location,
            "target": target,
            "status": "waiting",
            "items": items,
            "created_time": int(time.time() * 1000),
            "confirm_code":  confirm_code,
            "express_no": express_no,
            "pay": payment,
            "delivery_price": delivery_price,
            "comment": comment
        }
        if building_id:
            data['building_id'] = building_id
        subtask_id = yield cls.insert(data)
        raise gen.Return(subtask_id)

    @classmethod
    @gen.coroutine
    def MarkSubtasksStart(cls, subtask_ids):
        condition = {
            "_id": {"$in": subtask_ids},
        }
        setter = {
            "$set": {
                "status": "delivering",
                "start_time": int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, setter, multi=True)

    @classmethod
    @gen.coroutine
    def SetSubtasksScheduled(cls, subtask_ids, task_id):
        condition = {
            '_id': {
                '$in': subtask_ids
            },
            'status': {
                '$in': ['submitted', 'waiting']
            }
        }
        updater = {
            '$set': {
                'owner_task': task_id,
                'status': 'scheduled',
                'scheduled_time': int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, updater, multi=True)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def LockSubtaskForConfirm(cls, subtask_id):
        condition = {
            '_id': subtask_id
        }
        updater = {
            '$set': {
                'status': 'lock_for_confirm',
                'done_time': int(time.time() * 1000)
            }
        }
        result = yield cls.update(condition, updater)
        if result['updatedExisting'] and (result['ok'] == 1) and (result['nModified'] > 0):
            raise gen.Return(True)
        else:
            raise gen.Return(False)

    @classmethod
    @gen.coroutine
    def UnlockSubtaskAndSetToConfirmed(cls, subtask_id):
        condition = {
            '_id': subtask_id,
            'status': 'lock_for_confirm'
        }
        updater = {
            '$set': {
                'status': 'done',
                'done_time': int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetSubtasksStatus(cls, subtask_ids):
        condition = {
            "_id": {
                "$in": subtask_ids
            }
        }
        statuses = yield cls.find(condition, {"status": 1}).to_list(None)
        raise gen.Return(statuses)

    @classmethod
    @gen.coroutine
    def SetSubtasksDispatched(cls, subtask_ids):
        condition = {
            '_id': {
                '$in': subtask_ids
            },
            'status': {
                '$in': ['scheduled']
            }
        }
        updater = {
            '$set': {
                'status': 'dispatched',
                'dispatched_time': int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, updater, multi=True)
        raise gen.Return(result)
