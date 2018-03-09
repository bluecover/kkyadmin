#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/22/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
import json
from behaviors import BuildBanks
import logging


class CourierClear(RequestHandler):
    RequiredPrivilege = 'CourierClear'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        courier = yield self.courier_model.GetCourierFromId(courier_id)
        bank_data = yield BuildBanks().BuildBankData()
        data = {
            "courier": {
                "amount": courier.get('balance', 0) / 100.0
            },
            "bank_data": json.dumps(bank_data)
        }

        self.render('detail_page_courier_clear.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        type = self.get_argument('type')
        alipay_name = self.get_argument('alipay_name', '')
        alipay_account = self.get_argument('alipay_account', '')
        bank_account_name = self.get_argument('bank_account_name', '')
        bank_name = self.get_argument('bank_type', '')
        bank_account = self.get_argument('bank_no', '')
        bank_province = self.get_argument('bank_province', '')
        bank_city = self.get_argument('bank_city', '')
        bank_branch = self.get_argument('bank_name', '')
        bank_province_city = bank_province + bank_city
        comment = self.get_argument('comment', '')

        argument_right = True
        error_message = ''
        account = ''
        name = ''

        courier = yield self.courier_model.GetCourierFromId(courier_id)
        if courier['status'] == 'clear':
            argument_right = False
            error_message = '已经清算过'
        elif type == 'alipay':
            account = alipay_account
            name = alipay_name
            if not alipay_account or not alipay_name:
                argument_right = False
                error_message = '支付宝账户错误'
            bank_name = ''
            bank_province = ''
            bank_branch = ''
        elif type == 'bank':
            account = bank_account
            name = bank_account_name
            if not bank_name or not bank_account or not bank_province\
                or not bank_city or not bank_branch:
                argument_right = False
                error_message = '银行账户错误'
        else:
            argument_right = False
            error_message = '参数错误'

        bank_data = yield BuildBanks().BuildBankData()
        data = {
            "courier": {
                "amount": courier.get('balance', 0) / 100.0
            },
            "bank_data": json.dumps(bank_data)
        }

        if not argument_right:
            data['flag'] = 'error'
            data['message'] = error_message
            self.render('detail_page_courier_clear.html', data=data)
            raise gen.Return(None)
        

        result = yield self.courier_model.MinusWithdrawAndUpdateAccount(
            courier['_id'], type, account, name, courier['balance'],
            False, bank_name, bank_province, bank_branch
        )

        if result["updatedExisting"] and (result["ok"] == 1) and (result["nModified"] > 0):
            withdraw_id = yield self.withdraw_model.CreateWithdrawRecord(
                courier.get('district_id'), courier["_id"], type, account, name, courier['balance'],
                bank_name, bank_province_city, bank_branch
            )
            bill_id = yield self.bill_model.CreateWithdrawBill(courier["_id"], withdraw_id, courier['balance'])
            result = yield self.courier_model.update(
                { '_id': courier['_id'] },
                { '$set': { 'status': 'clear' } }
            )
            data['flag'] = 'ok'
            data['message'] = '清算成功'
        else:
            data['flag'] = 'error',
            data['message'] = '清算失败'

        self.render('detail_page_courier_clear.html', data=data)
