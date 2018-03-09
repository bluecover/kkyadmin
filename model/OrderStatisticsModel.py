#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/22/15'


from third_party.orm import Document
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
from third_party.orm.field import ObjectIdField
import settings
from tornado import gen


class OrderStatisticsModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'order_statistics'
    }

    date = StringField(required=True)
    school_id = ObjectIdField()
    school_name = StringField()
    region = StringField()
    province = StringField()
    city = StringField()
    unpaid = IntegerField()
    paid = IntegerField()
    sending = IntegerField()
    uncomment = IntegerField()
    done = IntegerField()
    cancel = IntegerField()
    refunded = IntegerField()
    item_price = IntegerField()
    delivery_price = IntegerField()
    discount_price = IntegerField()
