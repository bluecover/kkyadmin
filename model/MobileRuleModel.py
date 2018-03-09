#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8


''' (╯‵□′)╯︵┻━┻ '''
from tornado import gen
from third_party.orm import Document
from third_party.orm.field import MobileField
from third_party.orm.field import IntegerField
from third_party.orm.field import StringField
from third_party.orm.field import LocationField
from third_party.orm.field import ListField
from third_party.orm.field import ObjectIdField
import settings


class MobileRuleModel(Document):
    meta = {
        'db': settings.mongodb.SHARK_DB,
        'collection': 'mobile_rule'
    }

    prefix = IntegerField(required=True)
    province = StringField(required=True)
    city = StringField(required=True)
    type = StringField(required=True)

    @classmethod
    @gen.coroutine
    def GetMobileLocationInfo(cls, mobile):
        prefix = int(mobile[0:7])
        condition = {'prefix': prefix}
        info = yield cls.find_one(condition)
        raise gen.Return(info)
