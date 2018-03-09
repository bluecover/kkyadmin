#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '15-3-25'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from behaviors import ConvertText
from behaviors import BuildAreaData
from behaviors import BuildRoleData
from behaviors import HashPassword
from behaviors import BuildUserData
import json
from errors import PermissionDeny


class UserDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'UserRead' in self.current_user['privileges']:
            raise PermissionDeny()

        user_id = ObjectId(self.get_argument('id'))
        user = yield self.console_user_model.GetUserFromId(user_id)
        data = yield BuildUserData().BuildUserDetail(self.current_user, user)
        self.render('detail_page_member.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'UserUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        user_id = ObjectId(self.get_argument('id'))
        name = self.get_argument('name', None)
        mobile = self.get_argument('mobile', None)
        password = self.get_argument('pass', None)
        region = self.get_argument('area', None)
        province = self.get_argument('province', None)
        city = self.get_argument('city', None)
        school = self.get_argument('campus', None)
        note = self.get_argument('note', None)
        lock = self.get_argument('lock', None)

        user_data = {}
        if self._IsParamAvailable(name):
            user_data['name'] = name.encode('utf8')
        if self._IsParamAvailable(mobile):
            user_data['mobile'] = mobile
        if self._IsParamAvailable(password):
            user_data['password'] = HashPassword().Action(password.encode('utf8'))
        if self._IsParamAvailable(region):
            user_data['region'] = region.encode('utf8')
        if self._IsParamAvailable(province):
            user_data['province'] = province.encode('utf8')
        if self._IsParamAvailable(city):
            user_data['city'] = city.encode('utf8')
        if self._IsParamAvailable(city):
            user_data['school_name'] = school.encode('utf8')
        if self._IsParamAvailable(note):
            user_data['note'] = note.encode('utf8')
        if lock == 'lock':
            user_data['status'] = 'locked'
        elif lock =='unlock':
            user_data['status'] = 'normal'

        roles = []
        candidate_roles = yield BuildRoleData().BuildRoleCandidatesList()
        for cr in candidate_roles:
            if self.get_argument(cr['arg_name'].encode('utf8'), None) == 'on':
                roles.append(cr['arg_name'])
        user_data['roles'] = roles

        if school != u'全部校区':
            __school__ = yield self.school_model.GetSchoolFromName(school)
            user_data['school_id'] = __school__['_id']

        result = yield self.console_user_model.UpdateUserInfo(user_id, user_data)
        success = result['updatedExisting'] and result['ok'] == 1 and result['nModified'] > 0
        if success:
            data = {
                'flag': 'ok',
                'message': '修改用户资料成功'
            }
        else:
            data = {
                'flag': 'error',
                'message': '修改用户资料失败'
            }

        user = yield self.console_user_model.GetUserFromId(user_id)
        data = yield BuildUserData().BuildUserDetail(self.current_user, user)

        self.render('detail_page_member.html', data=data)


    def _IsParamAvailable(self, p):
        if p in [None, '', 'undefined', 'null', 'NULL', u'已和谐']:
            return False
        else:
            return True
