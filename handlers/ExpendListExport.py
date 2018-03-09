#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '6/5/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from behaviors import BuildAreaData
import json
from errors import PermissionDeny
import datetime
from kkytools.stat import expense
import time
from PermissionCheck import PermissionCheck
from settings import switch
from behaviors import CreateExpenseRecords

class ExpendListExport(RequestHandler):
    RequiredPrivilege = 'ExpendRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        data = {
            'areas': {
                'full': json.dumps(areas_with_schools)
            }
        }
        self.render('detail_page_expenses_export.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        action = self.get_argument('type')

        region = self.get_argument('area')
        province = self.get_argument('province')
        city = self.get_argument('city')
        school_name = self.get_argument('campus')

        date_start = self.get_argument('date_start')
        hour_start = self.get_argument('hour_start')
        minute_start = self.get_argument('minute_start')
        second_start = self.get_argument('second_start')

        date_end = self.get_argument('date_end')
        hour_end = self.get_argument('hour_end')
        minute_end = self.get_argument('minute_end')
        second_end = self.get_argument('second_end')

        email = self.get_argument('email')
        set_processed = self.get_argument('set_processed', '')

        start_dt = datetime.datetime.strptime(date_start, '%Y-%m-%d')
        start_dt += datetime.timedelta(hours=int(hour_start), minutes=int(minute_start), seconds=int(second_start))
        end_dt = datetime.datetime.strptime(date_end, '%Y-%m-%d')
        end_dt += datetime.timedelta(hours=int(hour_end), minutes=int(minute_end), seconds=int(second_end))

        data = {}

        if action == 'create':
            yield CreateExpenseRecords().Create(
                start_dt, end_dt,
                region, province, city, school_name
            )
            data = {
                'flag':'ok',
                'message':'生成支出记录成功'
            }
        elif action == 'export':
            self.queue.enqueue(
                expense.run,
                start_dt,
                end_dt,
                region, province, city, school_name,
                [email],
                set_processed,
                switch.DEBUG
            )
            data = {
                'flag':'ok',
                'message':'导出成功'
            }

        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        data['areas'] = {
            'full': json.dumps(areas_with_schools)
        }

        self.render('detail_page_expenses_export.html', data=data)
