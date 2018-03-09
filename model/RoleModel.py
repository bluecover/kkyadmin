#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/23/15'


import settings
from third_party.orm import Document
from third_party.orm.field import StringField
from third_party.orm.field import GenericListField
from tornado import gen


STATUS_CANDIDATS = [
    'normal',
    'locked'
]


class RoleModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'roles'
    }

    name = StringField(required=True)
    status = StringField(required=True, candidate=STATUS_CANDIDATS)
    text = StringField()
    privileges = GenericListField()

    @classmethod
    @gen.coroutine
    def GetRoleFromName(cls, name):
        condition = {
            'name': name
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewRole(cls, data):
        result = yield cls.insert(data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetRoleFromId(cls, role_id):
        condition = {
            '_id': role_id
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateRolePrivileges(cls, role_id, privileges):
        condition = {
            '_id': role_id
        }
        updater = {
            '$set': {
                'privileges': privileges
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def DeleteRole(cls, role_id):
        condition = {
            '_id': role_id
        }
        result = yield cls.remove(condition)
        raise gen.Return(result)
