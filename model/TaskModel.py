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
from third_party.orm import ObjectIdField
from third_party.orm import ListField
from third_party.orm import GenericListField
from third_party.orm import LocationField
from tornado import gen
import time
from bson import ObjectId
import time
import logging
import settings


TASK_STATUS = [
    'created',     # Created by our logistics system.
    'waiting',     # Ready to be assigned to a courier.
    'dispatched',  # Already assigned to a courier.
    'processing',  # The courier has started doing the task.
    'done',        # All the subtasks are delivered.
    'canceled'     # All the subtasks are canceled.
]


class ShopModel(EmbeddedDocument):
    _id = ObjectIdField()
    name = StringField()
    mobile = MobileField()
    address = StringField()
    location = LocationField()


class TaskModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'task'
    }
    status = StringField(required=True, default='created', candidate=TASK_STATUS)
    shop = EmbeddedDocumentField(ShopModel)
    subtasks = GenericListField(required=True)
    pay = IntegerField()
    created_time = IntegerField(required=True)
    dispatched_time = IntegerField()
    started_time = IntegerField()
    done_time = IntegerField()
    courier_id = ObjectIdField()
    courier_name = StringField()
    courier_mobile = StringField()
    district_id = ObjectIdField()
    district_name = StringField()
    next_dispatch_time = IntegerField()

    @classmethod
    @gen.coroutine
    def GetTaskFromId(cls, task_id):
        if isinstance(task_id, ObjectId) is False:
            task_id = ObjectId(task_id)
        result = yield cls.find_one({'_id': task_id})
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCourierTasks(cls, courier_id, limit, skip, status=None):
        if isinstance(courier_id, ObjectId) is False:
            courier_id = ObjectId(courier_id)
        condition = {
            'courier_id': courier_id
        }
        if isinstance(status, list):
            condition['status'] = {
                '$in': status
            }
        elif status:
            condition['status'] = status
        sort_condition = [
            ('created_time', -1)
        ]
        result = yield cls.find(condition).skip(skip).limit(limit).sort(sort_condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCourierTask(cls, courier_id, task_id):
        if not isinstance(courier_id, ObjectId):
            courier_id = ObjectId(courier_id)
        if not isinstance(task_id, ObjectId):
            task_id = ObjectId(task_id)
        condition = {
            '_id': task_id,
            'courier_id': courier_id
        }
        task = yield cls.find_one(condition)
        raise gen.Return(task)

    @classmethod
    @gen.coroutine
    def StartTask(cls, courier_id, task_id):
        condition = {
            "courier_id": courier_id,
            "_id": task_id
        }
        setter = {
            "$set": {
                "status": "processing",
                "started_time": int(time.time() * 1000)
            }
        }
        result = yield cls.update(condition, setter)

    @classmethod
    @gen.coroutine
    def CreateWaitingTask(cls, district_name, district_id, shop_id, shop_location, shop_name, shop_mobile, shop_address, subtask_ids):
        '''
        my_task = {
            'district_name': district_name,
            'district_id': district_id,
            'status': 'waiting',
            'shop': {
                '_id': shop_id,
                'location': shop_location,
                'name': shop_name,
                'mobile': shop_mobile,
                'address': shop_address
            },
            'subtasks': subtask_ids,
            'created_time': int(time.time()*1000)
        }

        logging.info(my_task)
        task_id =  yield cls.insert(my_task)
        raise gen.Return(task_id)
        '''
        condition = {
            'what_the_fuck': True,
            'created_time': int(time.time()*1000)
        }

        updater = {
            '$set': {
                'district_name': district_name,
                'district_id': district_id,
                'status': 'waiting',
                'shop': {
                    '_id': shop_id,
                    'location': shop_location,
                    'name': shop_name,
                    'mobile': shop_mobile,
                    'address': shop_address
                },
                'subtasks': subtask_ids,
                'created_time': int(time.time()*1000)
            }
        }

        result = yield cls.update(condition, updater, upsert=True)
        logging.info(result)
        raise gen.Return(result['upserted'])


    @classmethod
    @gen.coroutine
    def SetTaskDispatched(cls, task_id, my_courier):
        condition = {
            '_id': task_id,
            'status': 'waiting'
        }
        updater = {
            '$set': {
                'courier_id': my_courier['_id'],
                'status': 'dispatched',
                'dispatched_time': int(time.time()*1000),
                'courier_name': my_courier.get('name', ''),
                'courier_mobile': my_courier.get('mobile', '')
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def MarkTaskDone(cls, task_id):
        condition = {
            "_id": task_id
        }
        setter = {
            "$set": {
                "status": "done",
                "done_time": int(time.time()*1000)
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetTaskFromSubtaskId(cls, subtask_id):
        condition = {
            "subtasks": subtask_id
        }
        task = yield cls.find_one(condition)
        raise gen.Return(task)

    @classmethod
    @gen.coroutine
    def GetWaitingTasks(cls):
        condition = {
            'status': 'waiting'
        }
        tasks = yield cls.find(condition).to_list(None)
        raise gen.Return(tasks)

    @classmethod
    @gen.coroutine
    def SetTaskNextDispatchTime(cls, task_id, next_time):
        condition = {
            '_id': task_id
        }
        updater = {
            '$set': {
                'next_dispatch_time': next_time
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)
