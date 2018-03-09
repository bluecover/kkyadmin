#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '1/24/15'

from third_party.orm import Document
from third_party.orm import ObjectIdField
from third_party.orm import IntegerField
from third_party.orm import FloatField
from tornado import gen
import time
import settings

class LocationModel(Document):
    meta = {
        "db": settings.mongodb.WUKONG_DB,
        "collection": "location"
    }
    created_time = IntegerField(required=True)
    longitude = FloatField(required=True)
    latitude = FloatField(required=True)
    courier_id = ObjectIdField(required=True)

    @classmethod
    @gen.coroutine
    def LogCourierLocation(cls, courier_id, longitude, latitude):
        data = {
            "courier_id": courier_id,
            "longitude": longitude,
            "latitude": latitude,
            "created_time": int(time.time()*1000)
        }
        location_id = yield cls.insert(data)
        raise gen.Return(location_id)
