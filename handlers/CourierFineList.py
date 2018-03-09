#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/28/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from bson import ObjectId
from behaviors import ConvertText


class CourierFineList(RequestHandler):
    RequiredPrivilege = 'CourierAccountRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        courier_id = ObjectId(self.get_argument('id'))
        fines, _ = yield self.fine_model.GetFinesAndCountFromCourierId(courier_id)
        data = {
            'courier_id': courier_id,
            'thead': ['扣款金额', '扣款时间', '扣款说明'],
            'count': _,
            'datas': [
                [
                    {
                        'type': 'price',
                        'value': fine['amount'] / 100.0
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(fine['created_time'])
                    },
                    {
                        'type': 'text',
                        'value': fine.get('description', '')
                    }
                ] for fine in fines
            ]
        }
        self.render('detail_page_courier_fine_list.html', data=data)
