#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
import datetime
import time
from PermissionCheck import PermissionCheck
from behaviors import GodsGift
from behaviors import Push
import settings

class GiftContent(RequestHandler):
    RequiredPrivilege = 'GiveRedpacket'

    @gen.coroutine
    @PermissionCheck
    @LoginCheck
    def get(self, *args, **kwargs):
        data = {}
        self.render("helpdesk_gift.html", data=data)

    @gen.coroutine
    @PermissionCheck
    @LoginCheck
    def post(self, *args, **kwargs):
        description = self.get_argument('note', '').encode("UTF-8")
        mobile = self.get_argument('mobile', '').encode("UTF-8")
        order_id = self.get_argument('order_id', '')
        money = int(float(self.get_argument('amount')) * 100)
        confine = int(float(self.get_argument('limit')) * 100)
        count = int(self.get_argument('count', 1))
        name = self.get_argument('name', '').encode("UTF-8")
        push_notify = self.get_argument('push_notify', '')
        sms_notify = self.get_argument('sms_notify', '')
        push_content = self.get_argument('push_content', '')
        user_date_end = self.get_argument('user_date_end', '')
        with_device_token = self.get_argument('with_device_token', '')

        if self.current_user['name'] == 'sa' and '__gods_gift__' in description and not order_id:

            effect_date = datetime.datetime.strptime(self.get_argument('date_start'), '%Y-%m-%d')
            effect_time = int( time.mktime(effect_date.timetuple()) * 1000 )
            expiration_date = datetime.datetime.strptime(self.get_argument('date_end'), '%Y-%m-%d')
            expiration_date += datetime.timedelta(hours=23, minutes=59, seconds=59)
            expiration_time = int( time.mktime(expiration_date.timetuple()) * 1000 )

            user_condition = {}
            if with_device_token:
                user_condition = {
                    'device_token': { '$exists': True }
                }
            if user_date_end:
                user_date_end = datetime.datetime.strptime(user_date_end, '%Y-%m-%d')
                user_time_limit = int(time.mktime(user_date_end.timetuple()) * 1000)
                user_condition['created_time'] = { '$lt': user_time_limit }
            if mobile:
                user_condition['mobile'] = mobile

            kwargs = {
                'sms_notify': True if sms_notify else False,
                'push_notify': True if push_notify else False,
                'push_content': push_content
            }
            yield gen.Task(
                GodsGift().Give,
                user_condition,
                effect_time,
                expiration_time,
                money,
                confine,
                count,
                name,
                description,
                **kwargs
            )

            data = {
                "flag": "ok",
                "message": "Duang"
            }
            self.render("helpdesk_gift.html", data=data)

        else:

            if money > 500:
                data = {"flag": "error", "message": "红包金额过大"}
            else:
                effect_date = datetime.datetime.strptime(self.get_argument('date_start'), '%Y-%m-%d')
                effect_time = int( time.mktime(effect_date.timetuple()) * 1000 )
                expiration_date = datetime.datetime.strptime(self.get_argument('date_end'), '%Y-%m-%d')
                expiration_date += datetime.timedelta(hours=23, minutes=59, seconds=59)
                expiration_time = int( time.mktime(expiration_date.timetuple()) * 1000 )
                user = yield self.user_model.GetUserFromMobile(mobile)
                order = yield self.order_model.GetOrderFromId(ObjectId(order_id))
                if user and order:
                    description = "%s-%s-%s" % (str(self.current_user['_id']), str(order_id), description)
                    if isinstance(description, unicode):
                        description = description.encode("UTF-8")
                    coupon_id = yield self.coupon_model.CreateServiceCoupon(
                        user["_id"], description, money,
                        effect_time, expiration_time, confine)
                    logging.debug(coupon_id)
                    data = {
                        "flag": "ok",
                        "message": "Duang"
                    }

                    if push_notify:
                        device_token = user.get('device_token')
                        if device_token:
                            confine_p = int(confine/100) if confine % 100 == 0 else confine / 100.0
                            money_p = int(money/100) if money % 100 == 0 else money / 100.0
                            push_args = {
                                'data': '',
                                'content_args': (confine_p, money_p)
                            }
                            Push().Action(settings.push.USER_APP, device_token, settings.push.PUSH_GIVE_RED_PACKET, **push_args)

                else:
                    data = {
                        "flag": "error",
                        "message": "手機號碼不存在或订单ID不对 T_T"
                    }
            self.render("helpdesk_gift.html", data=data)
