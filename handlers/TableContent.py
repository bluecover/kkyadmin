#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from behaviors import BuildRoleData
from behaviors import BuildUserData
from behaviors import BuildSchoolData
from behaviors import BuildOrderData
from behaviors import BuildItemData
from behaviors import BuildShopData
from behaviors import BuildCourierData
from behaviors import BuildTaskData
from behaviors import BuildWithdrawData
from behaviors import BuildExpendData
from errors import PermissionDeny
import datetime
import time
import logging


class TableContent(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        type = self.get_argument('type')
        page = int(self.get_argument('page', 1))
        filter_type = self.get_argument('filter_type', '')
        filter_value = self.get_argument('filter_value', '')
        filter_status = self.get_argument('filter_status', '')
        filter_time_start = self.get_argument('filter_datestart', None)
        filter_time_end = self.get_argument('filter_dateend', None)
        area = self.get_argument('area', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        campus = self.get_argument('campus', '')

        if not area or u'全部' in area:
            area = self.current_user['region']
        if not province or u'全部' in province:
            province = self.current_user['province']
        if not city or u'全部' in city:
            city = self.current_user['city']
        if not campus or u'全部' in campus:
            campus = self.current_user['school_name']

        if filter_time_start:
            dt = datetime.datetime.utcfromtimestamp(int(filter_time_start)/1000)
            filter_time_start = int(time.mktime(dt.timetuple())) * 1000
        if filter_time_end:
            dt = datetime.datetime.utcfromtimestamp(int(filter_time_end)/1000) + datetime.timedelta(days=1)
            filter_time_end = int(time.mktime(dt.timetuple())) * 1000

        kwargs = {
            'page': page,
            'filter_type': filter_type,
            'filter_value': filter_value,
            'filter_status': filter_status,
            'filter_time_start': filter_time_start,
            'filter_time_end': filter_time_end,
            'area': area,
            'province': province,
            'city': city,
            'campus': campus
        }

        data = {}
        if type == 'role_list':
            if not 'RoleRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildRoleData().BuildTableContent(**kwargs)
        elif type == 'member_list':
            if not 'UserRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildUserData().BuildTableContent(**kwargs)
        elif type == 'campus_list':
            if not 'SchoolRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildSchoolData().BuildTableContent(**kwargs)
        elif type == 'order_list':
            if not 'OrderRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildOrderData().BuildTableContent(**kwargs)
        elif type == 'item_list':
            if not 'ItemRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildItemData().BuildTableContent(**kwargs)
        elif type == 'shop_list':
            if not 'ShopRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildShopData().BuildTableContent(**kwargs)
        elif type == 'courier_list':
            if not 'CourierRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildCourierData().BuildTableContent(**kwargs)
        elif type == 'task_list':
            if not 'TaskRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildTaskData().BuildTableContent(**kwargs)
        elif type == 'withdraw_list':
            if not 'WithdrawRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildWithdrawData().BuildTableContent(**kwargs)
        elif type == 'expenses_list':
            if not 'ExpendRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildExpendData().BuildTableContent(**kwargs)

        self.render('table_content.html', data=data)
