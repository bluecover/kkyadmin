#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from behaviors import BuildWithdrawData
from errors import PermissionDeny


class WithdrawDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'WithdrawRead' in self.current_user['privileges']:
            raise PermissionDeny()

        withdraw_id = ObjectId(self.get_argument('id'))
        withdraw_data = yield BuildWithdrawData().BuildWithdrawDetail(withdraw_id)
        data = {
            'withdraw': withdraw_data
        }
        self.render('detail_page_withdraw.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        process = self.get_argument('process', None)

        if process == 'true':

            if not 'WithdrawUpdate' in self.current_user['privileges']:
                raise PermissionDeny()
            withdraw_id = ObjectId(self.get_argument('id'))
            withdraw_data = yield BuildWithdrawData().BuildWithdrawDetail(withdraw_id)
            result = yield self.withdraw_model.MarkWithdrawProcessed(withdraw_id, '')
            success = result['updatedExisting'] and result['ok'] == 1 and result['nModified'] > 0
            if success:
                data = {
                    'flag': 'ok',
                    'message': '处理成功',
                    'withdraw': withdraw_data
                }
            else:
                data = {
                    'flag': 'error',
                    'message': '处理失败',
                    'withdraw': withdraw_data
                }
            self.render('detail_page_withdraw.html', data=data)

        else:
            self.write('')
