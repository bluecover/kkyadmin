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


class FineModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'fine'
    }

    courier_id = ObjectIdField(required=True)
    school_id = ObjectIdField(required=True)
    console_user_id = ObjectIdField(required=True)
    amount = IntegerField(required=True)
    created_time = IntegerField(required=True)
    reason = StringField()
    description = StringField()

    @classmethod
    @gen.coroutine
    def CreateFine(cls, fine_data):
        result = yield cls.insert(fine_data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetFinesAndCountFromCourierId(cls, courier_id, skip=None, limit=None):
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
