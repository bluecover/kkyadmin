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
from errors import PermissionDeny
from behaviors import BuildExpendData


class Table(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        table_type = self.get_argument('type')

        kwargs = {
            'user': self.current_user
        }

        data = {}
        if table_type == 'role_list':
            if not 'RoleRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = BuildRoleData().BuildTableFrame()
        elif table_type == 'member_list':
            if not 'UserRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildUserData().BuildTableFrame(**kwargs)
        elif table_type == 'campus_list':
            if not 'SchoolRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildSchoolData().BuildTableFrame(**kwargs)
        elif table_type == 'order_list':
            if not 'OrderRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildOrderData().BuildTableFrame(**kwargs)
        elif table_type == 'item_list':
            if not 'ItemRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = BuildItemData().BuildTableFrame(**kwargs)
        elif table_type == 'shop_list':
            if not 'ShopRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildShopData().BuildTableFrame(**kwargs)
        elif table_type == 'courier_list':
            if not 'CourierRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildCourierData().BuildTableFrame(**kwargs)
        elif table_type == 'task_list':
            if not 'TaskRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildTaskData().BuildTableFrame(**kwargs)
        elif table_type == 'withdraw_list':
            if not 'WithdrawRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildWithdrawData().BuildTableFrame(**kwargs)
        elif table_type == 'expenses_list':
            if not 'ExpendRead' in self.current_user['privileges']:
                raise PermissionDeny()
            data = yield BuildExpendData().BuildTableFrame(**kwargs)

        table_to_render = {
            'role_list': 'table_role.html',
            'item_list': 'table_role.html',
            'campus_list': 'table_campus.html'
        }.get(table_type, 'table.html')

        self.render(table_to_render, data=data)
