#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'


from tornado import gen
from third_party.orm import Document
from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
import settings


class CategoryModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'category'
    }

    name = StringField(required=True)
    priority = IntegerField(required=True, default=0)
    shop_id = ObjectIdField()

    @classmethod
    @gen.coroutine
    def GetCategoriesByIds(cls, category_ids):
        condition = {
            '_id': {
                '$in': category_ids
            }
        }
        categories = yield cls.find(condition).to_list(None)
        raise gen.Return(categories)

    @classmethod
    @gen.coroutine
    def GetCategoriesByShopId(cls, shop_id):
        condition = {
            "shop_id": shop_id
        }
        sort_condition = [
            ('priority', 1)
        ]
        categories = yield cls.find(condition).sort(sort_condition).to_list(None)
        raise gen.Return(categories)

    @classmethod
    @gen.coroutine
    def UpdateCategory(cls, category_id, **kw):
        condition = {
            '_id': category_id
        }
        fields = ['name', 'priority']
        updater = { '$set': {} }
        for f in fields:
            value = kw.get(f, None)
            if value:
                updater['$set'][f] = value
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewCategory(cls, shop_id, name, priority):
        data = {
            'shop_id': shop_id,
            'name': name,
            'priority': priority
        }
        category_id = yield cls.insert(data)
        raise gen.Return(category_id)
