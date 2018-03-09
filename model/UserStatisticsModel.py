#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '15-5-24'


from third_party.orm import Document
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
from third_party.orm.field import ObjectIdField
import settings
from tornado import gen


class UserStatisticsModel(Document):
    meta = {
        'db': settings.mongodb.CONSOLE_DB,
        'collection': 'user_statistics'
    }

    date = StringField(required=True)
    school_id = ObjectIdField()
    school_name = StringField()
    region = StringField()
    province = StringField()
    city = StringField()
    new_users = IntegerField()
    total_users = IntegerField()
