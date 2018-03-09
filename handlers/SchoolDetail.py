#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from bson import ObjectId
from errors import PermissionDeny
from behaviors import BuildSchoolData
import logging
from behaviors import SchoolCache


class SchoolDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'SchoolRead' in self.current_user['privileges']:
            raise PermissionDeny()

        school_id = ObjectId(self.get_argument('id'))
        data_campus = yield BuildSchoolData().BuildSchoolDetail(school_id)
        data = {
            'campus': data_campus
        }
        self.render('detail_page_campus.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'SchoolDelete' in self.current_user['privileges']:
            raise PermissionDeny()

        school_id = ObjectId(self.get_argument('id'))
        data_campus = yield BuildSchoolData().BuildSchoolDetail(school_id)

        _delete = self.get_argument('delete', None)
        if _delete == 'true':
            logging.critical('School Delete Attempt: id[%s], user[%s]' % (school_id, self.current_user['name']))
            condition = {
                'school_district': school_id
            }
            shops_count = yield self.shop_model.find(condition).count()
            if shops_count > 0:
                data = {
                    'campus': data_campus,
                    'flag': 'error',
                    'message': u'删除学校失败：这个学校还有商店！'
                }
                self.render('detail_page_campus.html', data=data)
            else:
                yield self.school_model.DeleteSchoolFromId(school_id)
                yield SchoolCache().Instance().DeleteSchool(school_id)
                logging.critical('School Delete Success: id[%s], user[%s]' % (school_id, self.current_user['name']))
                self.redirect('/table?type=campus_list')
        else:
            data = {
                'campus': data_campus
            }
            self.render('detail_page_campus.html', data=data)
