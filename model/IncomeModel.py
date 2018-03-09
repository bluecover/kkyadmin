#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '1/24/15'

from tornado import gen


from third_party.orm import Document
from third_party.orm import ObjectIdField
from third_party.orm import IntegerField
from tornado import gen
import settings

# Never insert data to this collection,
# an background program will run in background to update daily income everyday
class IncomeModel(Document):
    meta = {
        "db": settings.mongodb.WUKONG_DB,
        "collection": "income"
    }
    courier_id = ObjectIdField()
    datetime = IntegerField()
    money = IntegerField()

    @classmethod
    @gen.coroutine
    def ListIncome(cls, courier_id, limit, skip):
        query_condition = {
            "courier_id": courier_id
        }
        sort_condition = [
            ('datetime', -1)
        ]
        incomes = yield cls\
            .find(query_condition)\
            .limit(limit)\
            .skip(skip)\
            .sort(sort_condition)\
            .to_list(None)
        raise gen.Return(incomes)
