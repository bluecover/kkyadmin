#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/22/15'


from Behavior import Behavior
from tornado import gen
from BankCache import BankCache


class BuildBanks(Behavior):
    @gen.coroutine
    def BuildBankData(self):
        bank_data = yield BankCache.Instance().GetBanksData()
        raise gen.Return(bank_data)
