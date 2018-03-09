#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/7/15'


from Behavior import Behavior
from tornado import gen
import logging
from behaviors import SendSM
from settings import sms
from behaviors import Push
import settings


class GodsGift(Behavior):
    @gen.coroutine
    def Give(self, user_condition, effect_time, expiration_time, money,
             confine, count, name, description, **kwargs):
        all_users = yield self.user_model.find(user_condition).to_list(None)
        for user in all_users:

            exist_coupon = yield self.coupon_model.find_one(
                {
                    'user_id': user['_id'],
                    'description': description
                }
            )
            if exist_coupon:
                continue

            for i in range(0, count):
                coupon_id = yield self.coupon_model.CreateServiceCoupon(
                    user["_id"], description, money,
                    effect_time, expiration_time, confine,
                    name
                )
                logging.info('[GodsGift] _id: ' + str(coupon_id))

            if kwargs.get('push_notify') == True:
                device_token = user.get('device_token')
                if device_token:
                    push_args = {
                        'data': ''
                    }
                    content = kwargs.get('push_content')
                    if content:
                        push_args['content'] = content
                    Push().Action(settings.push.USER_APP, device_token, settings.push.PUSH_GODS_GIFT, **push_args)

            if kwargs.get('sms_notify') == True:
                sms_args = {}
                yield SendSM().Action(user['mobile'], sms.SMS_RED_PACKET, **sms_args)
