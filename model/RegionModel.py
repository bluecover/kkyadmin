#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/19/15'


from third_party.orm import Document
from third_party.orm import StringField
from third_party.orm import StringField
from third_party.orm import ObjectIdField
from third_party.orm import GenericListField
from third_party.orm import ListField
from third_party.orm import EmbeddedDocument
from third_party.orm import EmbeddedDocumentField
import settings
from tornado import gen


class CityModel(EmbeddedDocument):
    name = StringField(required=True)
    code = StringField()


class ProvinceModel(EmbeddedDocument):
    name = StringField(required=True)
    code = StringField()
    city = ListField(
        EmbeddedDocumentField(CityModel),
        required=True,
        default=[]
    )


class RegionModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'regions'
    }

    name = StringField(required=True)
    code = StringField()
    province = ListField(
        EmbeddedDocumentField(ProvinceModel),
        required=True,
        default=[]
    )

    @classmethod
    @gen.coroutine
    def AllRegions(cls):
        regions = yield cls.find({}).to_list(None)
        raise gen.Return(regions)
