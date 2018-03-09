#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildAreaData
import json
from behaviors import SchoolCache
from errors import ParamInvalidError


class SchoolCreate(RequestHandler):
    RequiredPrivilege = 'SchoolCreate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        areas = yield BuildAreaData().BuildAreas(self.current_user)
        data = {
            'areas': {
                'full': json.dumps(areas)
            }
        }
        self.render('detail_page_campus_edit.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        region = self.get_argument('area').encode('utf8')
        province = self.get_argument('province').encode('utf8')
        city = self.get_argument('city').encode('utf8')
        name = self.get_argument('name').encode('utf8')
        note = self.get_argument('note').encode('utf8')
        lng = float(self.get_argument('lng'))
        lat = float(self.get_argument('lat'))

        if '全部' in region or '全部' in province or '全部' in city:
            raise ParamInvalidError()

        conditon = {
            'name': name,
            'region': region,
            'province': province,
            'city': city,
        }
        updater = {
            '$set': {
                'name': name,
                'region': region,
                'province': province,
                'city': city,
                'note': note,
                'location': [lng, lat]
            }
        }

        result = yield self.school_model.update(conditon, updater, upsert=True)
        new_school_id = result.get('upserted')
        if new_school_id:
            school = yield self.school_model.GetSchoolFromId(new_school_id)
            yield SchoolCache().Instance().AddSchool(school)
            self.redirect('/campus_detail?id=%s' % new_school_id)
        else:
            areas = yield BuildAreaData().BuildAreas(self.current_user)
            data = {
                'flag': 'error',
                'message': '创建校区失败',
                'areas': {
                    'full': json.dumps(areas)
                }
            }
            if result.get('updatedExisting') == True:
                data['message'] += '：已存在相同校区'
            self.render('detail_page_campus_edit.html', data=data)
