#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


from third_party.orm import Document
from third_party.orm import StringField
from third_party.orm import LocationField
from third_party.orm import GenericListField
from tornado import gen
import logging
import settings


class SchoolModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        'collection': 'schools'
    }

    name = StringField(required=True)
    region = StringField()
    province = StringField()
    city = StringField()
    location = LocationField()
    note = StringField()

    dispatch_strategy = GenericListField()

    @classmethod
    @gen.coroutine
    def GetSchoolsFromProvince(cls, province):
        condition = {'province': province}
        result = yield cls.find(condition, {"name": 1}).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetSchoolsFromCity(cls, city):
        condition = { 'city': city }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetSchoolsAndCountFromArea(cls, skip=None, limit=None, region=None, province=None, city=None, school=None):
        condition = {}
        if region:
            condition['region'] = region
        if province:
            condition['province'] = province
        if city:
            condition['city'] = city
        if school:
            condition['name'] = school
        query = cls.find(condition)
        count = yield query.count()
        if skip is not None and limit is not None:
            schools = yield query.limit(limit).skip(skip).to_list(None)
        else:
            schools = yield query.to_list(None)
        result = (schools, count)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetSchoolFromName(cls, name):
        condition = {
            "name": name
        }
        school = yield cls.find_one(condition)
        logging.info(condition)
        logging.info(school)
        raise gen.Return(school)

    @classmethod
    @gen.coroutine
    def GetSchoolFromId(cls, schoold_id):
        condition = {
            '_id': schoold_id
        }
        result = yield cls.find_one(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetSchoolsFromLocation(cls, location, distance):
        condition = {
            "location": {
                "$geoWithin": {
                    "$center": [location, distance]
                }
            }
        }
        schools = yield cls.find(condition).to_list(None)
        raise gen.Return(schools)

    @classmethod
    @gen.coroutine
    def DeleteSchoolFromId(cls, schoold_id):
        condition = {
            '_id': schoold_id
        }
        result = yield cls.remove(condition)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateSchoolData(cls, school_id, school_data):
        condition = {
            '_id': school_id
        }
        updater = {
            '$set': school_data
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewSchool(cls, data):
        result = yield cls.insert(data)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetDispatchStrategy(cls, school_id, strategy):
        condition = {
            '_id': school_id
        }
        updater = {
            '$addToSet': {
                'dispatch_strategy': strategy
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def DeleteDispatchStrategy(cls, school_id, strategy):
        condition = {
            '_id': school_id
        }
        updater = {
            '$pull': {
                'dispatch_strategy': strategy
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)
