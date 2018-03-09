#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/21/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildAreaData
from behaviors import BuildOrderStatistics
from errors import PermissionDeny
from behaviors import BuildUserStatistics


class Analysis(RequestHandler):
    RequiredPrivilege = 'AnalysisRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        type = self.get_argument('type')
        mehtod = self.get_argument('method')

        data = {}
        if type == 'order':
            data = yield BuildOrderStatistics().BuildOrderStatisticsOfRegion(
                self.current_user,
                self.current_user['region'],
                self.current_user['province'],
                self.current_user['city'],
                self.current_user['school_name'],
                1
            )
        elif type == 'customer':
            data = yield BuildUserStatistics().BuildUserStatisticsOfRegion(
                self.current_user,
                self.current_user['region'],
                self.current_user['province'],
                self.current_user['city'],
                self.current_user['school_name'],
                1
            )

        if mehtod == 'simple':
            self.render('analysis_simple.html', data=data)
        else:
            pass


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        type = self.get_argument('type')
        mehtod = self.get_argument('method')
        region = self.get_argument('area', '')
        province = self.get_argument('province', '')
        city = self.get_argument('city', '')
        school_name = self.get_argument('campus', '')
        page = int(self.get_argument('page', 1))

        data = {}
        if type == 'order':
            data = yield BuildOrderStatistics().BuildOrderStatisticsOfRegion(
                self.current_user,
                region,
                province,
                city,
                school_name,
                page
            )
        elif type == 'customer':
            data = yield BuildUserStatistics().BuildUserStatisticsOfRegion(
                self.current_user,
                region,
                province,
                city,
                school_name,
                page
            )

        if mehtod == 'simple':
            self.render('analysis_simple.html', data=data)
        else:
            pass
