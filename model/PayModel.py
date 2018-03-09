#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '11/28/14'


from third_party.orm import Document
from third_party.orm.field import StringField
from third_party.orm.field import ObjectIdField
from third_party.orm.field import IntegerField
import time
from tornado import gen
import settings

class PayModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'pay'
    }
    order_id = ObjectIdField(required=True)
    trade_no = StringField(required=True)
    platform = StringField(
        required=True,
        candidate=['alipay', 'wechatpay']
    )
    created_time = IntegerField(required=True)

    wechat_openid = StringField()

    @classmethod
    @gen.coroutine
    def CreatePayRecord(cls, order_id, platform, trade_no, **kw):
        data = {
            'order_id': order_id,
            'trade_no': trade_no,
            'platform': platform,
            'created_time': int(time.time()*1000)
        }
        if platform == 'wechatpay':
            data['wechat_openid']= kw.get('wechat_openid', '')
        pay_id = yield cls.insert(data)
        raise gen.Return(pay_id)
