#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


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
from third_party.orm import GenericListField
from tornado import gen
from bson import ObjectId
import time
import math
import logging
import settings


COURIER_STATUS = [
    'unsubmitted',
    'verifying',
    'failed',
    'verified',
    'locked',
    'clear'
]

ACCOUNT_STATUS = [
    'normal',
    'locked'
]

class WeekScheduleModel(EmbeddedDocument):
    this = ObjectIdField()
    next = ObjectIdField()


class DeviceTokenModel(EmbeddedDocument):
    android = StringField()
    ios = StringField()


class AccountModel(EmbeddedDocument):
    type = StringField(required=True, candidate=['alipay', 'bank'])
    account_name = StringField(required=True)
    account_id = StringField(required=True)
    bank_name = StringField()
    bank_province_city = StringField()
    bank_branch = StringField()

class CourierModel(Document):
    meta = {
        'db': settings.mongodb.WUKONG_DB,    
        'collection': 'courier'
    }
    mobile = MobileField(required=True)
    name = StringField()
    birthday = StringField()
    graduate_year = IntegerField()
    qq = StringField()
    password = StringField()
    device_token = EmbeddedDocumentField(DeviceTokenModel)
    certificate_image = ObjectIdField()
    created_time = IntegerField()
    updated_time = IntegerField()
    schedule = EmbeddedDocumentField(WeekScheduleModel)
    account = ListField(EmbeddedDocumentField(AccountModel))
    balance = IntegerField()
    location = LocationField()
    school = StringField()
    status = StringField(required=True, candidate=COURIER_STATUS)
    shop_id = ObjectIdField()
    district_id = ObjectIdField()

    delivery_buildings = GenericListField()

    debt = IntegerField()
    account_status = StringField(candidate=ACCOUNT_STATUS)
    account_locked_time = IntegerField()
    account_unlocked_time = IntegerField()

    @classmethod
    @gen.coroutine
    def GetCourierFromId(cls, courier_id):
        if isinstance(courier_id, ObjectId) is False:
            courier_id = ObjectId(courier_id)
        result = yield cls.find_one({'_id': courier_id})
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetUserFromMobile(cls, mobile):
        courier = yield cls.find_one({'mobile': mobile})
        raise gen.Return(courier)


    @classmethod
    @gen.coroutine
    def CheckPassword(cls, mobile, password):
        condition = {
            'mobile': mobile,
            'password': password
        }
        courier = yield cls.find_one(condition)
        if courier:
            raise gen.Return(courier)
        else:
            raise gen.Return(False)

    @classmethod
    @gen.coroutine
    def CreateNewIfNotExists(cls, mobile):
        courier = yield cls.find_one({'mobile': mobile})
        if courier:
            raise gen.Return(False)
        else:
            now = int(time.time()*1000)
            courier_data = {
                'mobile': mobile,
                'created_time': now,
                'updated_time': now,
                'status': 'unsubmitted'
            }
            result = yield cls.insert(courier_data)
            raise gen.Return(True)

    @classmethod
    @gen.coroutine
    def UpdateDeviceToken(cls, courier_id, device_type, device_token):
        condition = {'_id': courier_id}
        updater = {
            '$set': {
                'device_token': {
                    device_type: device_token
                }
            }
        }
        yield cls.update(condition, updater)

    @classmethod
    @gen.coroutine
    def UpdateProfile(cls, courier_id, **kw):
        condition = {'_id': courier_id}
        updater = {'$set': {}}
        if 'name' in kw:
            updater['$set']['name'] = kw['name']
        if 'birthday' in kw:
            updater['$set']['birthday'] = kw['birthday']
        if 'school' in kw:
            updater['$set']['school'] = kw['school']
        if 'graduate_year' in kw:
            updater['$set']['graduate_year'] = kw['graduate_year']
        if 'qq' in kw:
            updater['$set']['qq'] = kw['qq']
        if 'certificate_image' in kw:
            updater['$set']['certificate_image'] = kw['certificate_image']
        if 'district_id' in kw:
            updater['$set']['district_id'] = kw['district_id']
        yield cls.update(condition, updater)

    @classmethod
    @gen.coroutine
    def UpdatePassword(cls, mobile, password):
        condition = {
            'mobile': mobile,
        }
        updater = {
            '$set': {
                'password': password
            }
        }
        yield cls.update(condition, updater)

    @classmethod
    @gen.coroutine
    def UpdateLocation(cls, courier_id, lgt, lat):
        condition = {
            '_id': courier_id
        }
        updater = {
            '$set': {
                'location': [lgt, lat]
            }
        }
        yield cls.update(condition, updater)

    @classmethod
    @gen.coroutine
    def GetScheduleId(cls, courier_id, week):
        condition = {
            '_id': courier_id
        }
        select = {
            'schedule': 1
        }
        sched = yield cls.find_one(condition, select)
        raise gen.Return(sched['schedule'][week])

    @classmethod
    @gen.coroutine
    def UpdateAccount(cls, mobile, account):
        condition = {
            'mobile': mobile
        }
        updater = {
            '$set': {
                'account': account
            }
        }
        yield cls.update(condition, updater)

    @classmethod
    @gen.coroutine
    def MinusWithdrawAndUpdateAccount(cls, courier_id, withdraw_type, account, name, money,
                                      update_account_flag, bank_name=None, bank_province_city=None, bank_branch=None):
        # check and update withdraw info first
        account_info = {
            "type": withdraw_type,
            "account_id": account,
            "account_name": name,
            "bank_name": bank_name,
            "bank_province_city": bank_province_city,
            "bank_branch": bank_branch
        }
        if update_account_flag:
            account_condition = {"_id": courier_id}
            account_setter = {
                "$push": {
                    "account": account_info
                }
            }
            account_update_result = yield cls.update(account_condition, account_setter)
            logging.info("[UPDATE WITHDRAW ACCOUNT] [%s,%s,%s]"%(str(courier_id), str(account_info), str(account_update_result)))

        withdraw_condition = {
            "_id": courier_id,
            "balance": {
                "$gte": money
            }
        }
        withdraw_setter = {
            "$inc": {
                "balance": 0 - int(math.fabs(money))
            }
        }
        withdraw_result = yield cls.update(withdraw_condition, withdraw_setter)
        logging.critical("[WITHDRAW] [%s,%s,%s]", str(courier_id), str(money), str(withdraw_result))
        raise gen.Return(withdraw_result)

    @classmethod
    @gen.coroutine
    def ListWithdrawInfo(cls, courier_id):
        query_condition = {"_id": courier_id}
        select_condition = {"account": 1}
        result = yield cls.find_one(query_condition, select_condition)
        retval = result.get('account', [])
        raise gen.Return(retval)

    @classmethod
    @gen.coroutine
    def UpdatePasswordFromMobileAndSetStatusToVerifying(cls, mobile, password):
        condition = {
            'mobile': mobile
        }
        setter = {
            '$set': {
                'password': password,
                'status': 'verifying'
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def SetVerifyingAfterFirstProfileUpdate(cls, courier_id):
        condition = {
            "_id": courier_id,
            "status": {
                '$in': ["unsubmitted", "failed"]
            }
        }
        setter = {
            "$set": {
                "status": "verifying"
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCouriersFromIds(cls, courier_ids):
        condition = {
            '_id': {
                '$in': courier_ids
            }
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCouriersFromShopId(cls, shop_id):
        condition = {
            'shop_id': shop_id,
            'status': 'verified'
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetNearbyCouriers(cls, location, distance):
        condition = {
            'location': {
                '$geoWithin': {
                    '$center': [location, distance]
                }
            },
            'status': 'verified'
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def AddMoneyToCourierBalance(cls, courier_id, money):
        condition = {
            '_id': courier_id
        }
        updater = {
            '$inc': {
                'balance': money
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def GetCouriersFromDistrictId(cls, district_id):
        condition = {
            'district_id': district_id,
            'status': 'verified'
        }
        result = yield cls.find(condition).to_list(None)
        raise gen.Return(result)


    @classmethod
    @gen.coroutine
    def SetVerified(cls, courier_id, result):
        condition = {
            '_id': courier_id
        }
        setter = {
            '$set': {
                'status': 'verified' if result else 'failed'
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateDeliveryBuildings(cls, courier_id, building_ids):
        condition = {
            '_id': courier_id
        }
        setter = {
            '$set': {
                'delivery_buildings': building_ids
            }
        }
        result = yield cls.update(condition, setter)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateAccountStatus(cls, courier_id, locked):
        condition = {
            '_id': courier_id
        }
        updater = {
            '$set': {
                'account_status': 'locked' if locked else 'normal'
            }
        }
        if locked:
            updater['$set']['account_locked_time'] = int(time.time()*1000)
        else:
            updater['$set']['account_unlocked_time'] = int(time.time()*1000)
        result = yield cls.update(condition, updater)
        raise gen.Return(result)


    @classmethod
    @gen.coroutine
    def SetDebt(cls, courier_id, new_debt):
        condition = {
            '_id': courier_id
        }
        updater = {
            '$set': {
                'debt': new_debt
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def UpdateDebt(cls, courier_id, debt_change):
        condition = {
            '_id': courier_id
        }
        updater = {
            '$inc': {
                'debt': int(debt_change)
            }
        }
        result = yield cls.update(condition, updater)
        raise gen.Return(result)
