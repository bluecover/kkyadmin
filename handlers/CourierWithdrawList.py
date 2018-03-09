#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '15-5-31'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from bson import ObjectId
from behaviors import ConvertText


class CourierWithdrawList(RequestHandler):
    RequiredPrivilege = 'CourierAccountRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        expends, _ = yield self.expend_model.GetExpendsAndCountFromCourierId(courier_id)
        withdraw_expend_data = []
        for expend in expends:
            withdraw = yield self.withdraw_model.GetWithdrawFromId(expend['withdraw_id'])
            withdraw_expend_data.append(
                [
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawTypeToChinese(withdraw['account_type'])
                    },
                    {
                        'type': 'price',
                        'value': expend['withdraw_amount']/100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(expend['created_time'])
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().WithdrawStatusToChinese(expend['status']),
                    },
                    {
                        'type': 'price',
                        'value': expend['real_amount']/100.0
                    }
                ]
            )
        data = {
            'courier_id': courier_id,
            'thead': ['提现方式', '金额', '提现时间', '状态', '实际打款'],
            'datas': withdraw_expend_data,
            'count': _
        }
        self.render('detail_page_courier_withdraw_list.html', data=data)
