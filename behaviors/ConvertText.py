#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


import datetime


class ConvertText(object):
    def RoleStatusToChinese(self, status):
        return {
            'normal': u'正常',
            'locked': u'锁定'
        }.get(status, '')

    def RoleStatusColor(self, status):
        return {
            'normal': 'green',
            'locked': 'red'
        }.get(status, '')

    def UserStatusToChinese(self, status):
        return {
            'normal': u'正常',
            'locked': u'锁定'
        }.get(status, '')

    def UserStatusColor(self, status):
        return {
            'normal': 'green',
            'locked': 'red'
        }.get(status, '')

    def OrderStatusToChinese(self, status):
        return {
            'unpaid': u'未支付',
            'cancel': u'已取消',
            'paid': u'已支付',
            'sending': u'配送中',
            'uncomment': u'已收货',
            'done': u'已完成',
            'refunded': u'已退款'
        }.get(status, '')

    def OrderStatusColor(self, status):
        return {
            'unpaid': 'orange',
            'paid': 'pink',
            'sending': 'blue',
            'uncomment': 'darkblue',
            'done': 'green',
            'cancel': 'red',
            'refunded': 'grey'
        }.get(status, '')


    def TimestampToText(self, timestamp):
        if timestamp == 0:
            return ''
        timestamp = int(timestamp/1000)
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y年%m月%d日 %H:%M:%S')

    def ItemStatusToChinese(self, status):
        return {
            'on_sale': u'在售',
            'off_shelves': u'下架',
            'on': u'在售',
            'off': u'下架',
            'deleted': u'已删除'
        }.get(status, '')

    def     ItemStatusColor(self, status):
        return {
            'on_sale': u'green',
            'off_shelves': u'grey',
            'on': u'green',
            'off': u'grey',
            'deleted': u'red'
        }.get(status, '')

    def ShopStatusToChinese(self, status):
        return {
            'open': u'营业中',
            'closed': u'休息中',
            'out': u'已关闭'
        }.get(status, '')

    def ShopStatusColor(self, status):
        return {
            'open': u'green',
            'closed': u'grey',
            'out': u'red'
        }.get(status, '')

    def ShopTypeToChinese(self, status):
        return {
            'cvs': u'便利店',
            'restaurant': u'饭店',
            'fruit': u'水果',
            'canteen': u'食堂',
            'drink': u'饮品',
            'express': u'代取快递',
            'laundry': u'洗衣',
            'cigarette': u'烟'
        }.get(status, '')

    def ShopTypeChineseToEnglish(self, type):
        return {
            u'便利店': 'cvs',
            u'饭店': 'restaurant'
        }.get(type, '')

    def CourierStatusToChinese(self, status):
        return {
            'unsubmitted': u'未提交资料',
            'verifying': u'审核中',
            'failed': u'审核失败',
            'verified': u'已审核',
            'locked': u'锁定',
            'clear': u'已清算'
        }.get(status, '')

    def CourierStatusColor(self, status):
        return {
            'unsubmitted': u'blue',
            'verifying': u'orange',
            'failed': u'red',
            'verified': u'green',
            'locked': u'purple',
            'clear': u'pink'
        }.get(status, '')

    def CourierAccountStatusToChinese(self, status):
        return {
            'normal': u'正常',
            'locked': u'冻结'
        }.get(status, '')

    def TaskStatusToChinese(self, status):
        return {
            'waiting': u'等待分配',
            'scheduled': u'等待分配',
            'dispatched': u'已分配速递员',
            'processing': u'正在配送',
            'done': u'已完成'
        }.get(status, '')

    def TaskStatusColor(self, status):
        return {
            'waiting': u'orange',
            'dispatched': u'blue',
            'processing': u'darkblue',
            'done': u'green'
        }.get(status, '')

    def WithdrawStatusToChinese(self, status):
        return {
            'processed': u'已处理',
            'unprocessed': u'未处理',
            'freezed': u'冻结'
        }.get(status, '')

    def WithdrawStatusColor(self, status):
        return {
            'processed': u'green',
            'unprocessed': u'orange',
            'freezed': u'red'
        }.get(status, '')

    def WithdrawTypeToChinese(self, type):
        return {
            'alipay': u'转到支付宝',
            'bank': u'转到银行'
        }.get(type, '')

    def PayMethodToChinese(self, method):
        return {
            'alipay': u'支付宝',
            'wechatpay': u'微信'
        }.get(method, '')

    def OrderRefundReasonToChinese(self, r):
        return {
            'do_not_want': u'用户不要了',
            'user_info_error': u'用户信息错误',
            'school_location_error': u'校区定位错误',
            'dispatch_not_in_time': u'未及时配送',
            'dispatch_error': u'卡单'
        }.get(r, '')

    def OrderHurryReasonToChinese(self, r):
        return {
            'no_available_courier': u'无速递员排班',
            'courier_do_not_send': u'速递员不送',
            'courier_lose_contact': u'速递员联系不上',
            'already_delivered': u'已送达',
            'other': u'其他'
        }.get(r, '')
