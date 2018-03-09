#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
""""""

from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
from third_party.orm.field import ListField
from third_party.orm import Document
from tornado import gen
import settings
import time
from pymongo.helpers import DuplicateKeyError


class BuildingModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'building'
    }
    name = StringField(required=True, unique=True)
    school_id = ObjectIdField(required=True)

    @classmethod
    @gen.coroutine
    def CreateBuilding(cls, name, school_id):
        data = {
            "name": name,
            "school_id": school_id
        }
        condition = data
        try:
            building_id = yield cls.insert(condition, data, upsert=True)
            raise gen.Return(building_id)
        except DuplicateKeyError:
            building = yield cls.find_one(data)
            raise gen.Return(building['_id'])

    @classmethod
    @gen.coroutine
    def GetSchoolBuildings(cls, school_id):
        condition = {
            "school_id": school_id
        }
        buildings = yield cls.find(condition).sort([('name', 1)]).to_list(None)
        raise gen.Return(buildings)


    @classmethod
    @gen.coroutine
    def GetBuildingFromId(cls, building_id):
        condition = {
            '_id': building_id
        }
        building = yield cls.find_one(condition)
        raise gen.Return(building)

    @classmethod
    @gen.coroutine
    def GetBuildingFromIds(cls, building_ids):
        condition = {
            '_id': {
                '$in': building_ids
            }
        }
        buildings = yield cls.find(condition).sort([('name', 1)]).to_list(None)
        raise gen.Return(buildings)
