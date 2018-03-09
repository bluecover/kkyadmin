#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from bson import ObjectId
from behaviors import BuildAreaData
import json
from behaviors import SchoolCache


class SchoolEdit(RequestHandler):
    RequiredPrivilege = 'SchoolUpdate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        school_id = ObjectId(self.get_argument('id'))
        school = yield self.school_model.GetSchoolFromId(school_id)
        areas = yield BuildAreaData().BuildAreas(self.current_user)
        data = {
            'campus': {
                '_id': school['_id'],
                'area': school.get('region', ''),
                'province': school.get('province', ''),
                'city': school.get('city', ''),
                'campus': school.get('name', ''),
                'note': school.get('note', ''),
                'position': school.get('location', [0,0])
            },
            'areas': {
                'full': json.dumps(areas),
                'choosed': json.dumps(
                    {
                        'area': school.get('region', ''),
                        'province': school.get('province', ''),
                        'city': school.get('city', '')
                    }
                )
            }
        }
        self.render('detail_page_campus_edit.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        school_id = ObjectId(self.get_argument('id'))
        region = self.get_argument('area').encode('utf8')
        province = self.get_argument('province').encode('utf8')
        city = self.get_argument('city').encode('utf8')
        name = self.get_argument('name').encode('utf8')
        note = self.get_argument('note').encode('utf8')
        lng = float(self.get_argument('lng'))
        lat = float(self.get_argument('lat'))

        existing_school = yield self.school_model.GetSchoolFromName(name)
        if existing_school and existing_school['_id'] != school_id:
            data = {
                'flag': 'error',
                'message': '修改学校信息失败：已有同名学校！'
            }
            self.render('detail_page_campus_edit.html', data=data)
            raise gen.Return(None)

        new_school_data = {
            'name': name,
            'region': region,
            'province': province,
            'city': city,
            'note': note,
            'location': [lng, lat]
        }
        result = yield self.school_model.UpdateSchoolData(school_id, new_school_data)
        if result['updatedExisting'] and result['ok'] == 1 and result['nModified'] > 0:
            school = yield self.school_model.GetSchoolFromId(school_id)
            yield SchoolCache().Instance().UpdateSchool(school)
            self.redirect('/campus_detail?id=%s' % school_id)
        else:
            data = {
                'flag': 'error',
                'message': '修改学校信息失败'
            }
            self.render('detail_page_campus_edit.html', data=data)
