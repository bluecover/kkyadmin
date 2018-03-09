#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '15-3-25'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildRoleData
from behaviors import HashPassword
from behaviors import  BuildAreaData
import json
import re
from errors import ParamInvalidError


class UserCreate(RequestHandler):
    RequiredPrivilege = 'UserCreate'
    PASSWORD_REGEX = re.compile(r"^[0-9a-zA-Z\!\?\@\#\$\%\^\&\*\(\)\[\]\{\}\|\\]{6,64}$", re.IGNORECASE)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        candidates_roles = yield BuildRoleData().BuildRoleCandidatesList()
        area_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
        data = {
            'roles': [
                {
                    'display_name': u'候选角色',
                    'sub_roles': candidates_roles
                },
            ],
            'areas': {
                'full': json.dumps(area_full)
            }
        }
        self.render('detail_page_member_add.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        name = self.get_argument('name').strip().encode('utf8')
        realname = self.get_argument('realname', '').strip()
        password = self.get_argument('pass').strip()
        mobile = self.get_argument('mobile', '').strip()
        region = self.get_argument('area').encode('utf8')
        province = self.get_argument('province').encode('utf8')
        city = self.get_argument('city').encode('utf8')
        school = self.get_argument('campus').encode('utf8')
        note = self.get_argument('note', '').encode('utf8')

        if not name or not password or not mobile:
            raise ParamInvalidError()

        roles = []
        candidate_roles = yield BuildRoleData().BuildRoleCandidatesList()
        for cr in candidate_roles:
            if self.get_argument(cr['arg_name'], None) == 'on':
                roles.append(cr['arg_name'])

        if not self._ValidatePassword(password):
           area_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
           data = {
               'roles': [{
                   'display_name': u'候选角色',
                   'sub_roles': candidate_roles
               }],
               'areas': {
                   'full': json.dumps(area_full)
               },
               'flag': 'error',
               'message': '创建新用户失败 密码不合法'
           }
           self.render('detail_page_member_add.html', data=data)
           raise gen.Return(None)

        user_data = {
            'name': name,
            'password': HashPassword().Action(password),
            'status': 'normal',
            'mobile': mobile,
            'roles': roles,
            'region': region,
            'province': province,
            'city': city,
            'school_name': school,
            'note': note,
            'realname': realname
        }

        if school != '全部校区':
            __school__ = yield self.school_model.GetSchoolFromName(school)
            user_data['school_id'] = __school__['_id']

        result, user_id = yield self.console_user_model.CreateNewUser(user_data)

        if result == 'created':
            self.redirect('/member_detail?id=%s' % user_id)
        else:
            error_info = ''
            if result == 'updated':
                error_info = '用户名已存在'
            area_full = yield BuildAreaData().BuildAreasWithSchools(self.current_user)
            data = {
                'roles': [
                    {
                        'display_name': u'候选角色',
                        'sub_roles': candidate_roles
                    },
                ],
                'areas': {
                    'full': json.dumps(area_full)
                },
                'flag': 'error',
                'message': '创建新用户失败 ' + error_info
            }
            self.render('detail_page_member_add.html', data=data)

    def _ValidatePassword(self, password):
        if not self.PASSWORD_REGEX.match(password):
            return False
        else:
            return True
