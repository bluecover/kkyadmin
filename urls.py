#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


import handlers


URLS = [
    ('/', handlers.Index),
    ('/login', handlers.Login),
    ('/logout', handlers.Logout),
    ('/dashboard', handlers.Dashboard),
    ('/dashboard_content', handlers.DashboardContent),

    ('/table', handlers.Table),
    ('/table_content', handlers.TableContent),

    ('/role', handlers.RoleList),
    ('/role_detail', handlers.RoleDetail),
    ('/role_add', handlers.RoleCreate),

    ('/member', handlers.UserList),
    ('/member_detail', handlers.UserDetail),
    ('/member_add', handlers.UserCreate),

    ('/campus', handlers.SchoolList),
    ('/campus_detail', handlers.SchoolDetail),
    ('/campus_edit', handlers.SchoolEdit),
    ('/campus_add', handlers.SchoolCreate),

    ('/shop', handlers.ShopList),
    ('/shop_detail', handlers.ShopDetail),
    ('/shop_edit', handlers.ShopEdit),
    ('/shop_add', handlers.ShopCreate),
    ('/shop_edit_items', handlers.ShopEditItems),
    ('/shop_edit_items_content', handlers.ShopEditItemsContent),
    ('/shop_delete', handlers.ShopDelete),

    ('/item', handlers.ItemList),
    ('/item_detail', handlers.ItemDetail),
    ('/item_add', handlers.ItemCreate),

    ('/order', handlers.OrderList),
    ('/order_detail', handlers.OrderDetail),

    ('/courier', handlers.CourierList),
    ('/courier_detail', handlers.CourierDetail),
    ('/courier_workhour', handlers.CourierWorkhour),
    ('/courier_workhour_content', handlers.CourierWorkhourContent),
    ('/courier_clear', handlers.CourierClear),
    ('/courier_account', handlers.CourierAccount),
    ('/courier_account_withholding_add', handlers.CourierFineAdd),
    ('/courier_fine_list', handlers.CourierFineList),
    ('/courier_withdraw_list', handlers.CourierWithdrawList),

    ('/helpdesk_authcode', handlers.CodeQuery),
    ('/helpdesk_authcode_content', handlers.CodeQueryContent),
    ('/helpdesk_gift', handlers.Gift),
    ('/helpdesk_gift_content', handlers.GiftContent),


    ('/task', handlers.TaskList),
    ('/task_detail', handlers.TaskDetail),
    ('/task_forward', handlers.TaskForward),

    ('/withdraw', handlers.WithdrawList),
    ('/withdraw_detail', handlers.WithdrawDetail),

    ('/shop_edit_items_types_item_list', handlers.ShopEditItemsOwn),

    ('/building', handlers.Building),
    ('/building_content', handlers.BuildingContent),
    ('/building_couriers', handlers.BuildingCouriers),

    ('/analysis', handlers.Analysis),
    ('/analysis_order', handlers.AnalysisOrder),
    ('/analysis_customer', handlers.AnalysisUser),

    ('/expenses', handlers.ExpendList),
    ('/expenses_detail', handlers.ExpendDetail),
    ('/expenses_export', handlers.ExpendListExport)
]
