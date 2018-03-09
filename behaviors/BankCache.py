#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/22/15'


from tornado import gen
from Behavior import Behavior
from settings import bank as bank_settings


class BankCache(Behavior):
    def __init__(self):
        super(BankCache, self).__init__()
        self.__banks__ = None

    @staticmethod
    def Instance():
        if not hasattr(BankCache, '__instance__'):
            BankCache.__instance__ = BankCache()
        return BankCache.__instance__

    @gen.coroutine
    def GetBanksData(self):
        if not self.__banks__:
            self.__banks__ = yield self._BuildBanksData()
        raise gen.Return(self.__banks__)

    @gen.coroutine
    def _BuildBanksData(self):
        city_id_dict = {}
        for city in bank_settings.CITIES:
            city_id_dict[city['cityId']] = city
        bank_id_dict = {}
        for bank in bank_settings.BANKS:
            bank_id_dict[bank['id']] = bank

        banks_d = {}
        branches = yield self.branches_model.find({}).to_list(None)
        for branch in branches:
            city = city_id_dict.get(branch['cityId'])
            if not city:
                continue
            bank = bank_id_dict.get(branch['bankId'])
            if not bank:
                continue
            province_d = banks_d.setdefault(bank['name'], {})
            city_d = province_d.setdefault(city['province'], {})
            bank_l = city_d.setdefault(city['name'], [])
            bank_l.append(branch['name'])

        bank_data = [
            {
                'name': bank_name,
                'provinces': [
                    {
                        'name': province_name,
                        'cities': [
                            {
                                'name': city_name,
                                'banks': bank_l
                            } for city_name, bank_l in city_d.items()
                        ]
                    } for province_name, city_d in province_d.items()
                ]
            } for bank_name, province_d in banks_d.items()
        ]

        raise gen.Return(bank_data)
