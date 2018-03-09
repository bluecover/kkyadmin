#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2/12/15'

import time
from tornado import gen
from third_party.orm.document import Document
from third_party.orm.field import ObjectIdField
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
import settings


class FeedbackModel(Document):
    collection = {
        "db": settings.mongodb.SHARK_DB,
        "meta": "feedback"
    }
    user_id = ObjectIdField()
    created_time = IntegerField(required=True)
    feedback = StringField(required=True)
    contact = StringField(required=True)

    @classmethod
    @gen.coroutine
    def CreateNewComment(cls, user_id, contact, feedback):
        condition = {
            "feedback": feedback,
            "contact": contact
        }
        setter = {
            "$set": {
                "feedback": feedback,
                "contact": contact,
                "created_time": int(time.time() * 1000)
            }
        }
        yield cls.update(condition, setter, upsert=True)

    @classmethod
    @gen.coroutine
    def GetComments(cls, limit=20, skip=0):
        sort_condition = [
            ('created_time', -1)
        ]
        comments = yield cls.find({}).sort(sort_condition).to_list(None)
        raise gen.Return(comments)
