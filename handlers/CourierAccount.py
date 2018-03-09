#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from errors import PermissionDeny
from behaviors import BuildCourierData
from bson import ObjectId
import decimal
import time


class CourierAccount(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'CourierAccountRead' in self.current_user['privileges']:
            raise PermissionDeny()

        courier_id = ObjectId(self.get_argument('id'))
        data = yield BuildCourierData().BuildCourierAccountData(courier_id)
        self.render('detail_page_courier_account.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'CourierAccountUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        courier_id = ObjectId(self.get_argument('id'))
        # debt = self.get_argument('debt', '')
        freeze = self.get_argument('freeze', '')

        if freeze == 'freeze':
            result = yield self.courier_model.UpdateAccountStatus(courier_id, True)
        elif freeze == 'unfreeze':
            result = yield self.courier_model.UpdateAccountStatus(courier_id, False)
            # Set 'freezed' expense record to 'unprocessed'
            condition = {
                'courier_id': courier_id,
                'status': 'freezed'
            }
            updater = {
                '$set': {
                    'status': 'unprocessed',
                    'created_time': int(time.time() * 1000)
                }
            }
            result = yield self.expend_model.update(
                condition,
                updater,
                multi=True
            )

        '''
        if debt:
            debt = int(decimal.Decimal(self.get_argument('debt'))*100)
            # TODO: lock update
            result = yield self.courier_model.SetDebt(courier_id, debt)
        '''

        data = yield BuildCourierData().BuildCourierAccountData(courier_id)
        data['flag'] = 'ok'
        data['message'] = '修改成功'
        self.render('detail_page_courier_account.html', data=data)
