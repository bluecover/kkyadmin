#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
import settings
from behaviors import BuildRoleData
from errors import PermissionDeny
from behaviors import ConvertText


class RoleDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'RoleRead' in self.current_user['privileges']:
            raise PermissionDeny()

        role_id = ObjectId(self.get_argument('id'))
        role = yield self.role_model.GetRoleFromId(role_id)
        role_privileges = role['privileges']
        data = {
            'role': {
                'name': role['text'],
                '_id': role['_id'],
                'status': ConvertText().RoleStatusToChinese(role['status']),
                'permissions': BuildRoleData().BuildPrivileges(role_privileges)
            }
        }
        self.render('detail_page_role.html', data=data)


    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'RoleUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        role_id = ObjectId(self.get_argument('id'))
        _delete = self.get_argument('delete', None)
        if _delete == 'true':
            yield self.role_model.DeleteRole(role_id)
            self.redirect('/table?type=role_list')
        else:
            new_privileges = []
            for privilege_group in settings.role.PRIVILEGES:
                for p in privilege_group['privileges']:
                    if self.get_argument(p['name'], None) == 'on':
                        new_privileges.append(p['name'])

            yield self.role_model.UpdateRolePrivileges(role_id, new_privileges)
            role = yield self.role_model.GetRoleFromId(role_id)
            data = {
                'role': {
                    'name': role['text'],
                    '_id': role['_id'],
                    'status': ConvertText().RoleStatusToChinese(role['status']),
                    'permissions': BuildRoleData().BuildPrivileges(role['privileges'])
                }
            }
            self.render('detail_page_role.html', data=data)


    def _BuildPrivilegesData(self, role_privileges):
        privileges_data = []
        for privilege_group in settings.role.PRIVILEGES:
            perm = {
                'name': privilege_group['text'],
                'sub_permissions': [
                    {
                        'name': p['text'],
                        'arg_name': p['name'],
                        'checked': True if p['name'] in role_privileges else False
                    } for p in privilege_group['privileges']
                ]
            }
            privileges_data.append(perm)
        return privileges_data
