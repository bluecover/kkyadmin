# -*- coding:utf-8 -*-

__all__ = ['dumps', 'loads']

from bson import ObjectId
from datetime import datetime, date, time
import json

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return super(JSONEncoder, self).default(obj)


def dumps(obj):
    return json.dumps(obj, cls=JSONEncoder)


def loads(obj):
    return json.loads(obj)
