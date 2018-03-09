#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
import settings
from behaviors import BuildRoleData


class RoleCreate(RequestHandler):
    RequiredPrivilege = 'RoleCreate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            'role': {
                'permissions': BuildRoleData().BuildPrivileges([])
            }
        }
        self.render('detail_page_role_add.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        role_name = self.get_argument('name')
        existed_role = yield self.role_model.GetRoleFromName(role_name)
        if existed_role:
            data = {
                'flag': 'error',
                'message': u'已存在相同名字的角色'
            }
            self.render('detail_page_role_add.html', data=data)
        else:
            privileges = []
            for privilege_group in settings.role.PRIVILEGES:
                for p in privilege_group['privileges']:
                    if self.get_argument(p['name'], None) == 'on':
                        privileges.append(p['name'])
            role = {
                'name': role_name,
                'text': role_name,
                'status': 'normal',
                'privileges': privileges
            }

            new_role_id = yield self.role_model.CreateNewRole(role)

            if new_role_id:
                '''
                data = {
                    'flag': 'ok',
                    'message': u'创建成功'
                }
                self.render('detail_page_role_add.html', data=data)
                '''
                self.redirect('/role_detail?id=%s' % new_role_id)
            else:
                data = {
                    'flag': 'error',
                    'message': u'出错了(原因我也不知道)'
                }
                self.render('detail_page_role_add.html', data=data)
