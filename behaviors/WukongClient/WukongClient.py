#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'

from ..Behavior import Behavior
from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from settings import wukong
import urllib
import json
import logging
import time
from third_party import superjson

from settings.switch import DEBUG
_DEBUG_DEFAULT_DISTRICT_ID = "54fbe54f8f87c17753edfce6"
_RELEASE_DEFAULT_DISTRICT_ID = None
DEFAULT_DISTRICT_ID = _DEBUG_DEFAULT_DISTRICT_ID if DEBUG else _RELEASE_DEFAULT_DISTRICT_ID

class WukongClient(Behavior):
    __ACCESS_TOKEN_NAMESPACE__ = "__WUKONG_CLIENT_ACCESS_TOKEN__"
    __ACCESS_TOKEN_LOCK_KEY__ = "__WUKONG_CLIENT_ACCESS_TOKEN_LOCK__"
    __ACCESS_TOKEN_LOCK_TTL__ = 20
    __REQUEST_MAX_TRY__ = 10

    @gen.coroutine
    def CreateNewExpress(self, order):
        access_token = yield self.GetAccessToken()
        shop = yield self.shop_model.GetShopFromId(order['shop_id'])
        formated_items = yield self.FormatItems(order["items"])
        building_id = order.get('building_id', None)
        if not building_id:
            building_id = ""
        else:
            building_id = str(building_id)
        data = {
            "order_id": str(order["_id"]),
            "app_id": wukong.APP_ID,
            "receiver_name": order["receiving"]["name"].encode("UTF-8"),
            "receiver_mobile" :order["receiving"]["mobile"].encode("UTF-8"),
            "receiver_address" :order["receiving"]["address"].encode("UTF-8"),
            "receiver_location" : superjson.dumps(order["receiving"]["location"]),
            "building_id": building_id,
            "shop_id" : str(shop['_id']),
            "shop_name" : shop["name"].encode("UTF-8"),
            "shop_mobile" : shop["mobile"].encode("UTF-8"),
            "shop_address" : shop["address"].encode("UTF-8"),
            "shop_location" : superjson.dumps(shop["location"]),
            "express_no": str(order["_id"]),
            "items" : superjson.dumps(formated_items),
            "district_id": str(shop.get("school_district", DEFAULT_DISTRICT_ID)),
            "payment": order.get("items_price", 0),
            "delivery_price": order.get("delivery_price", 0),
            "comment": order.get("remark", u"").encode("UTF-8")
        }

        school_id = shop.get("school_district", None)
        if not school_id:
            logging.info("shop school id empty: " + str(shop['_id']))
            raise gen.Return(None)
        school = yield self.school_model.find_one({'_id': school_id})
        district_name = school['name']
        data['district_name'] = district_name.encode('utf8')
        logging.info(district_name)


        client = AsyncHTTPClient()
        for i in range(self.__REQUEST_MAX_TRY__):
            data['access_token'] = access_token
            response = yield client.fetch(wukong.EXPRESS_NEW_URL, method="POST", body=urllib.urlencode(data), validate_cert=False)
            result = json.loads(response.body)
            if result['flag'] == 'error':
                logging.critical(result)
                logging.critical("fail to do request")
                access_token = yield self.RefreshAccessToken()
                if i < self.__REQUEST_MAX_TRY__:
                    continue
                else:
                    raise gen.Return(False)
            else:
                express_id = result['data']["_id"]
                logging.info("create new express %s successfully" % express_id.encode("UTF-8") )
                raise gen.Return(express_id)

    @gen.coroutine
    def QueryExpress(self, express_id):
        if isinstance(express_id, unicode):
            express_id = express_id.encode("UTF-8")
        data = {
            "app_id": wukong.APP_ID,
            "stid": express_id
        }
        client = AsyncHTTPClient()
        access_token = yield self.GetAccessToken()
        for i in range(self.__REQUEST_MAX_TRY__):
            data['access_token'] = access_token
            response = yield client.fetch(wukong.EXPRESS_STATUS_URL, method="POST", body=urllib.urlencode(data), validate_cert=False)
            result = json.loads(response.body)
            if result['flag'] == "error":
                logging.critical("fail to do request")
                access_token = yield self.RefreshAccessToken()
                continue
            else:
                raise gen.Return(result['data'])

    @gen.coroutine
    def NotifyExpressDone(self, express_id, coupon=0):
        if isinstance(express_id, unicode):
            express_id = express_id.encode("UTF-8")
        else:
            express_id = str(express_id)
        token = yield self.GetAccessToken()
        data = {
            "app_id": wukong.APP_ID,
            "subtask_id": express_id,
            "subtask_coupon": coupon
        }
        for i in range(self.__REQUEST_MAX_TRY__):
            client = AsyncHTTPClient()
            data['access_token'] = token
            response = yield client.fetch(wukong.EXPRESS_DONE_URL, method="POST", body=urllib.urlencode(data), validate_cert=False)
            result = json.loads(response.body)
            if result['flag'] == 'error':
                logging.critical("NotifyExpressDone fail: %s, %d" % (express_id, coupon))
                token = yield self.RefreshAccessToken()
                continue
            else:
                logging.info("NotifyExpressDone success: %s, %d" % (express_id, coupon))
                break

    @gen.coroutine
    def FormatItems(self, order_items):
        formated_items = []
        items = yield self.item_model.GetItemsFromIds([item["_id"] for item in order_items])
        item_map = {}
        for item in items:
            item_map[str(item["_id"])] = item
        for order_item in order_items:
            item_id_str = str(order_item["_id"])
            item = item_map[item_id_str]
            formated_item = {
                "name": item["name"],
                "_id": item_id_str,
                "image_id": str(item["image_id"]),
                "count": order_item["num"],
                "price": order_item["price"],
                "description": item.get("description", "")
            }
            formated_items.append(formated_item)
        raise gen.Return(formated_items)

    @gen.coroutine
    def GetAccessToken(self):
        token = yield gen.Task(self.async_redis.get, self.__ACCESS_TOKEN_NAMESPACE__)
        if not token:
            token = yield self.RefreshAccessToken()
        raise gen.Return(token)

    @gen.coroutine
    def RefreshAccessToken(self):
        old_token = yield gen.Task(self.async_redis.get, self.__ACCESS_TOKEN_NAMESPACE__)
        lock = self.async_redis.lock(self.__ACCESS_TOKEN_LOCK_KEY__, lock_ttl=self.__ACCESS_TOKEN_LOCK_TTL__)
        yield gen.Task(lock.acquire, blocking=True)
        token = yield gen.Task(self.async_redis.get, self.__ACCESS_TOKEN_NAMESPACE__)
        if (token is None) or (token == old_token):
            client = AsyncHTTPClient()
            data = {
                "app_id": wukong.APP_ID,
                "app_secret": wukong.APP_SECRET
            }
            response = yield client.fetch(wukong.ACCESS_TOKEN_URL, method="POST", body=urllib.urlencode(data), validate_cert=False)
            result = json.loads(response.body)
            if result['flag'] == 'error':
                logging.critical("**** INVALID APP_ID OR APP_SECRET ****")
            else:
                token = result['data']['access_token']
                deadline = int( int(result['data']['deadline'] / 1000))
                ttl = deadline - int(time.time())
                yield gen.Task(self.async_redis.set, self.__ACCESS_TOKEN_NAMESPACE__, token)
                yield gen.Task(self.async_redis.expire, self.__ACCESS_TOKEN_NAMESPACE__, ttl)
        lock.release()
        raise gen.Return(token)



