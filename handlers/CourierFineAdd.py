#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from bson import ObjectId
import decimal
import time


class CourierFineAdd(RequestHandler):
    RequiredPrivilege = 'CourierAccountUpdate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        data = {
            'courier': {
                '_id': courier_id
            }
        }
        self.render('detail_page_courier_account_withholding_add.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        withholding_money = int(decimal.Decimal(self.get_argument('withholding_money'))*100)
        withholding_description = self.get_argument('withholding_description')
        courier = yield self.courier_model.GetCourierFromId(courier_id)
        reuslt = yield self.fine_model.CreateFine(
            {
                'courier_id': courier_id,
                'school_id': courier['district_id'],
                'console_user_id': self.current_user['_id'],
                'amount': withholding_money,
                'description': withholding_description,
                'created_time': int(time.time()*1000)
            }
        )

        result = yield self.courier_model.UpdateDebt(courier_id, withholding_money)

        data = {
            'courier': {
                '_id': courier_id
            },
            'flag': 'ok',
            'message': '添加成功'
        }
        self.render('detail_page_courier_account_withholding_add.html', data=data)
