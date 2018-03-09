#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'


from third_party.orm.field import StringField
from third_party.orm.field import IntegerField
from third_party.orm.field import ObjectIdField
from third_party.orm import Document
from tornado import gen
import settings


class ItemModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'item'
    }

    category = ObjectIdField(required=True)
    name = StringField(required=True)
    price = IntegerField(required=True)
    created_time = IntegerField(required=True)
    status = StringField(
        required=True,
        default='on_sale',
        candidate=['on_sale', 'off_shelves', 'deleted']
    )

    shop_id = ObjectIdField()
    image_id = ObjectIdField()
    description = StringField()
    priority = IntegerField()

    # Tue May  5 12:36:35 CST 2015
    # Since version 0,4, limit and special_price
    limit = IntegerField(required=True, default=0) # 0 => does not limit, >0 => buy limit
    special_price = IntegerField(required=True, default=0)

    @classmethod
    @gen.coroutine
    def GetItemsFromShopAndCategoryV1ToV3(cls, shop_id, category_id):
        '''Tue May  5 12:29:46 CST 2015
        if client's API version is lower than 0.4, we should not return any
        special items. Although it is a workaround way to implement so, I do
        not have any better idea now.
        '''
        condition = {
            'shop_id': shop_id,
            'category': category_id,
            'old': {
                '$exists': False
            },
            'status': "on_sale",
            "limit": {"$exists": False} # the only different query condition with GetItemsFromShopAndCategory
        }
        items = yield cls.find(condition).to_list(None)
        raise gen.Return(items)

    @classmethod
    @gen.coroutine
    def GetItemsFromShopAndCategory(cls, shop_id, category_id, limit=8192, skip=0):
        condition = {
            'shop_id': shop_id,
            'category': category_id,
            'old': {
                '$exists': False
            },
            'status': "on_sale"
        }
        items = yield cls.find(condition).limit(limit).skip(skip).to_list(None)
        raise gen.Return(items)

    @classmethod
    @gen.coroutine
    def GetItemsFromShopV1ToV3(cls, shop_id):
        condition = {
            'shop_id': shop_id,
            'old': {
                '$exists': False
            },
            'limit': {"$exists": False} # please refer GetItemsFromShopAndCategoryV1ToV3
        }
        items = yield cls.find(condition).to_list(None)
        raise gen.Return(items)

    @classmethod
    @gen.coroutine
    def GetItemsFromShop(cls, shop_id, limit=8192, skip=0):
        condition = {
            'shop_id': shop_id,
            'old': {
                '$exists': False
            }
        }
        items = yield cls.find(condition).limit(limit).skip(skip).to_list(None)
        raise gen.Return(items)

    @classmethod
    @gen.coroutine
    def GetItemFromId(cls, item_id):
        condition = {
            '_id': item_id
        }
        item = yield cls.find_one(condition)
        raise gen.Return(item)

    @classmethod
    @gen.coroutine
    def GetItemsFromIds(cls, item_ids):
        if not item_ids or not isinstance(item_ids, list):
            raise gen.Return([])
        condition = {
            '_id': {
                '$in': item_ids
            }
        }
        items = yield cls.find(condition).to_list(None)
        raise gen.Return(items)

    @classmethod
    @gen.coroutine
    def UpdateItem(cls, item_id, **kw):
        condition = {
            '_id': item_id
        }
        fields = ['category_id', 'name', 'price', 'description', 'image_id', 'priority']
        updater = { '$set': {} }
        for f in fields:
            value = kw.get(f, None)
            if value:
                updater['$set'][f] = value
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def CreateNewItem(cls, item):
        item_id = yield cls.insert(item)
        raise gen.Return(item_id)
