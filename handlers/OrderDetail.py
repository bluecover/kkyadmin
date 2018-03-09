#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/26/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from errors import PermissionDeny
from behaviors import BuildOrderData
from behaviors import WukongClient
from behaviors import RefundOrder
from behaviors import Push
import settings


class OrderDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'OrderRead' in self.current_user['privileges']:
            raise PermissionDeny()

        order_id = ObjectId(self.get_argument('id'))
        order = yield self.order_model.GetOrderFromId(order_id)
        data = yield BuildOrderData().BuildOrderDetail(order)
        self.render('detail_page_order.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        order_id = ObjectId(self.get_argument('id'))
        confirm = self.get_argument('confirm', '')
        refund = self.get_argument('refund', '')
        send_to_wukong = self.get_argument('send_to_wukong', '')
        go_to_task = self.get_argument('go_to_task', '')
        hurry = self.get_argument('hurry', '')

        if confirm == 'true':
            if not 'OrderConfirm' in self.current_user['privileges']:
                raise PermissionDeny()
            order = yield self.order_model.GetOrderFromId(order_id)
            if order['status'] in ['sending']:
                yield self.order_model.SetOrderConfirmed(None, order_id)
                express_id = order.get('express_id', None)
                if express_id:
                    client = WukongClient()
                    yield client.NotifyExpressDone(express_id, order.get('items_price', 0))

        if refund == 'true':
            if not 'OrderRefund' in self.current_user['privileges']:
                raise PermissionDeny()
            result = yield RefundOrder().Action(order_id)
            if result:
                order_subtask = yield self.subtask_model.find_one(
                    {
                        'express_no': str(order_id)
                    }
                )
                if order_subtask and 'owner_task' in order_subtask:
                    task = yield self.task_model.find_one(
                        {
                            '_id': order_subtask['owner_task']
                        }
                    )
                    courier_id = task.get('courier_id')
                    if courier_id:
                        courier = yield self.courier_model.find_one({'_id': courier_id})
                        device_token = courier.get('device_token')
                        if device_token:
                            push_args = {
                                'data': str(task['_id'])
                            }
                            Push().Action(settings.push.COURIER_APP, device_token, settings.push.PUSH_CONSOLE_SUBTASK_CANCEL, **push_args)

            refund_reason = self.get_argument('refund_reason', '')
            refund_detail = self.get_argument('refund_detail', '')
            record = yield self.order_refund_model.find_one({'order_id': order_id})
            if not record:
                result = yield self.order_refund_model.UpdateRecord(order_id, refund_reason, refund_detail)


        if send_to_wukong == 'true':
            if not 'OrderSend' in self.current_user['privileges']:
                raise PermissionDeny()
            order = yield self.order_model.GetOrderFromId(order_id)
            if order['status'] == 'paid' and not order.get('express_id', ''):
                client = WukongClient()
                express_id = yield client.CreateNewExpress(order)
                yield self.order_model.SetOrderExpressId(order['_id'], express_id)

        if go_to_task == 'true':
            if not 'TaskRead' in self.current_user['privileges']:
                raise PermissionDeny()
            order = yield self.order_model.GetOrderFromId(order_id)
            subtask_id = order.get('express_id')
            if subtask_id:
                task = yield self.task_model.find_one(
                    {
                        'subtasks': subtask_id
                    }
                )
                self.redirect('/task_detail?id=%s' % str(task['_id']))

        if hurry == 'true':
            hurry_reason = self.get_argument('hurry_reason', '')
            hurry_detail = self.get_argument('hurry_detail', '')
            result = yield self.order_hurry_model.CreateRecord(order_id, hurry_reason, hurry_detail)

        # order = yield self.order_model.GetOrderFromId(order_id)
        # data = yield BuildOrderData().BuildOrderDetail(order)
        # self.render('detail_page_order.html', data=data)
        self.redirect('/order_detail?id=%s' % str(order_id))
