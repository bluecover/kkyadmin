#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


from third_party.orm import Document
from third_party.orm import IntegerField
from third_party.orm import ObjectIdField
from tornado import gen
from bson import ObjectId
import settings

class ScheduleModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'schedule'
    }
    courier = ObjectIdField(required=True)
    start = IntegerField(required=True)  # timestamp in second
    end = IntegerField(required=True)    # timestamp in second

    @classmethod
    @gen.coroutine
    def GetScheduleFromId(cls, schedule_id):
        condition = {
            '_id': schedule_id
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCourierSchedulesInInterval(cls, courier_id, start, end):
        condition = {
            'courier': courier_id,
            'start': {
                '$gte': start
            },
            'end': {
                '$lte': end
            }
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateSchedule(cls, courier_id, start, end, set):
        condition = {
            'courier': courier_id,
            'start': start,
            'end': end
        }
        if set:
            updater = {
                '$set': {
                    'courier': courier_id,
                    'start': start,
                    'end': end
                }
            }
            result = yield cls.update(condition, updater, upsert=True)
        else:
            result = yield cls.remove(condition)
        raise gen.Return(True)

    @classmethod
    @gen.coroutine
    def GetAvailableCourierSchedules(cls, cids, current_time_sec):
        condition = {
            'courier': {
                '$in': cids
            },
            'start': {
                '$lte': current_time_sec
            },
            'end': {
                '$gte': current_time_sec
            }
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)
