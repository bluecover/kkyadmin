#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2/12/15'


from tornado import gen
from third_party.orm import Document
from third_party.orm.field import MobileField
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
from third_party.orm.field import LocationField
from third_party.orm.field import ListField
from third_party.orm.field import ObjectIdField
import settings


SHOP_STATUS_CANDIDATE = [
    'open',
    'closed',
    'out'
]

SHOP_TYPE_CANDIDATE = [
    'cvs',          # 便利店
    'restaurant',   # 饭店
    'fruit',        # 水果
    'canteen',      # 食堂
    'drink',        # 饮品
    'express',      # 代取快递
    'laundry',      # 洗衣
    'cigarette'     # 烟
]


class ShopModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'shop'
    }

    name = StringField(required=True)
    mobile = MobileField(required=True)
    location = LocationField(required=True)
    address = StringField(required=True)
    status = StringField(required=True, candidate=SHOP_STATUS_CANDIDATE)
    created_time = IntegerField(required=True)
    school_district = ObjectIdField(required=True)

    open_hour = ListField(IntegerField())
    image_id = ObjectIdField()
    delivery_price = IntegerField()
    min_cost_to_deliver = IntegerField()
    type = StringField(candidate=SHOP_TYPE_CANDIDATE)
    description = StringField()
    bulletin_message = StringField()

    region = StringField()
    province = StringField()
    city = StringField()
    school_name = StringField()

    @classmethod
    @gen.coroutine
    def GetNearbyShops(cls, location, distance, limit, skip):
        condition = {
            'location': {
                '$geoWithin': {
                    '$center': [location, distance]
                }
            },
            'status': 'open'
        }
        result = yield cls.find(condition).skip(skip).limit(limit).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetShopFromId(cls, shop_id):
        condition = {
            '_id': shop_id
        }
        shop = yield cls.find_one(condition)
        raise gen.Return(shop)

    @classmethod
    @gen.coroutine
    def GetShopsBySchoolDistrict(cls, district_id, limit, skip):
        condition = {
            'school_district': district_id,
            'status': 'open'
        }
        result = yield cls.find(condition).skip(skip).limit(limit).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateShop(cls, shop_id, shop_data):
        condition = {
            '_id': shop_id
        }
        updater = {
            '$set': shop_data
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)
