#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/8/15'


from third_party.orm import Document
from third_party.orm import StringField
from third_party.orm import GenericListField
from third_party.orm import ObjectIdField
from third_party.orm import MobileField
from third_party.orm import ValidateError
from pymongo.helpers import DuplicateKeyError
from tornado import gen
import settings


STATUS_CANDIDATES = [
    'normal',
    'locked'
]


class ConsoleUserModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'users'
    }

    # must add unique index of name in the database
    name = StringField(min_length=1, max_length=32, required=True, unique=True)
    password = StringField(required=True)
    status = StringField(required=True, candidate=STATUS_CANDIDATES)
    roles = GenericListField()
    mobile = MobileField(required=True)
    note = StringField()
    realname = StringField(min_length=1, max_length=32, required=True)

    region = StringField()
    province = StringField()
    city = StringField()
    school_name = StringField()
    school_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def CheckPassword(cls, name, pass_hash):
        condition = {
            'name': name,
            'password': pass_hash
        }
        user = yield cls.find_one(condition)
        raise gen.Return(user)

    @classmethod
    @gen.coroutine
    def GetUserFromId(cls, user_id):
        condition = {
            '_id': user_id
        }
        user = yield cls.find_one(condition)
        raise gen.Return(user)

    @classmethod
    @gen.coroutine
    def GetUsersFromStatus(cls, status):
        condition = {
            'status': status
        }
        users = yield cls.find(condition).to_list(None)
        raise gen.Return(users)

    @classmethod
    @gen.coroutine
    def GetUsersAndCountFromArea(cls, skip=None, limit=None, region=None, province=None, city=None, school_name=None,
                                 other_condition=None):
        condition = {}
        if region:
            condition['region'] = region
        if province:
            condition['province'] = province
        if city:
            condition['city'] = city
        if school_name:
            condition['school_name'] = school_name
        if other_condition:
            for k,v in other_condition.items():
                condition[k] = v
        query = cls.find(condition)
        count = yield query.count()
        if skip is not None and limit is not None:
            users = yield query.limit(limit).skip(skip).to_list(None)
        else:
            users = yield query.to_list(None)
        result = (users, count)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewUser(cls, data):
        condition = {
            'name': data['name']
        }
        result = yield cls.update(condition, data, upsert=True)
        new_user_id = result.get('upserted')
        if new_user_id:
            raise gen.Return(('created', new_user_id))
        elif result.get('updatedExisting') == True:
            raise gen.Return(('updated', None))
        else:
            raise gen.Return(('failed', None))

    @classmethod
    @gen.coroutine
    def UpdateUserInfo(cls, user_id, user_data):
        condition = {
            '_id': user_id
        }
        updater = {
            '$set': user_data
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetUsersByName(cls, name):
        condition = {
            'name': name
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)
