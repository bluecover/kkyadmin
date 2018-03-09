#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '1/30/15'

from third_party.orm import Document
from third_party.orm import EmbeddedDocument
from third_party.orm import EmbeddedDocumentField
from third_party.orm import IntegerField
from third_party.orm import StringField
from third_party.orm import MobileField
from third_party.orm import ObjectIdField
from third_party.orm import ListField
from third_party.orm import FloatField
from third_party.orm import LocationField
from tornado import gen
from bson import ObjectId
import time
import math
import logging
import settings


class BranchesModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,
        "collection": "branches"
    }
    cityId = IntegerField(required=True)
    name = StringField(required=True)
    bankId = IntegerField(required=True)


    @classmethod
    @gen.coroutine
    def ListCityBranches(cls, cid, bid):
        condition = {
            "cityId": cid,
            "bankId": bid
        }
        branches = yield cls.find(condition).to_list(None)
        raise gen.Return(branches)