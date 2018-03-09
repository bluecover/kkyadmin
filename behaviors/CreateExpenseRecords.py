#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '6/10/15'


from Behavior import Behavior
from tornado import gen
import time


class CreateExpenseRecords(Behavior):
    @gen.coroutine
    def Create(self, start_dt, end_dt, region, province, city, school_name):
        start_timestamp = int(time.mktime(start_dt.timetuple()) * 1000)
        end_timestamp = int(time.mktime(end_dt.timetuple()) * 1000)
        time_condition = {
            'created_time': {
                '$gte': start_timestamp,
                '$lt': end_timestamp
            }
        }


        if region == u'全部大区':
            region = None
        if province == u'全部省份':
            province = None
        if city == u'全部城市':
            city = None
        if school_name == u'全部校区':
            school_name = None
        if not region and not province and not city and not school_name:
            school_condition = {}
        else:
            schools, _ = yield self.school_model.GetSchoolsAndCountFromArea(
                region=region,
                province=province,
                city=city,
                school=school_name
            )
            school_condition = {
                'school_id': {
                    '$in': [s['_id'] for s in schools]
                }
            }

        condition = dict(time_condition.items() + school_condition.items())
        condition['status'] = 'unprocessed'

        withdraws = yield self.withdraw_model.find(condition).sort([('created_time', -1)]).to_list(None)

        for withdraw in withdraws:
            courier = yield self.courier_model.GetCourierFromId(withdraw.get('courier_id'))
            if not courier:
                continue

            withdraw_amount = withdraw['money']
            debt_amount = courier.get('debt', 0)

            if debt_amount < 0:  # OOPS!
                debt_amount = 0

            if withdraw_amount > debt_amount:  # Enough withdraw amount to clear current debt.
                fine_amount = debt_amount
                expend_amount = withdraw_amount - debt_amount
                debt_change = 0 - int(debt_amount)
            else:  # Expend 0, pay debt only.
                fine_amount = withdraw_amount
                expend_amount = 0
                debt_change = 0 - int(withdraw_amount)

            if fine_amount != 0:
                find_bill_id = yield self.bill_model.CreateFineBill(courier['_id'], withdraw['_id'], fine_amount)

            # Create expend record for THIS withdraw.
            account_status = courier.get('account_status')
            if account_status == 'locked':
                expense_status = 'freezed'
            else:
                expense_status = 'unprocessed'
            expend_id = yield self.expend_model.CreateExpendRecord(
                courier['_id'],
                courier.get('name', ''),
                withdraw['_id'],
                withdraw_amount,
                fine_amount,
                expend_amount,
                courier.get('district_id'),
                expense_status
            )

            # Update courier debt.
            result = yield self.courier_model.UpdateDebt(courier['_id'], debt_change)

            # Set withdraw to 'processed'
            result = yield self.withdraw_model.MarkWithdrawProcessed(withdraw['_id'], '')
