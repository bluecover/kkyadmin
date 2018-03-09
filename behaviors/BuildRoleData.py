#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/25/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
import settings


class BuildRoleData(Behavior):
    def BuildTableFrame(self):
        data = {
            'filters': {
                'types': {
                    'name': u'角色名',
                },
                'status': {
                    'normal': u'正常',
                    'locked': u'锁定',
                }
            },
            'extra_btns': [
                {
                    'text': u'添加角色',
                    'href': '/role_add'
                }
            ],
            'table_src': 'role_list'
        }
        return data

    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'name':
            condition['text'] = kw.get('filter_value')
        status = kw.get('filter_status', None)
        if status:
            condition['status'] = status
        roles = yield self.role_model.find(condition).to_list(None)
        datas = []
        for r in roles:
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': r['text']
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().RoleStatusToChinese(r['status']),
                        'color': ConvertText().RoleStatusColor(r['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/role_detail?id=%s")' % str(r['_id'])
                    }
                ]
            )
        data = {
            'thead': [u'角色', u'状态', u'操作'],
            'datas': datas,
            'count': len(datas)
        }
        raise gen.Return(data)

    def BuildPrivileges(self, role_privileges):
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

    @gen.coroutine
    def BuildRoleCandidatesList(self):
        condition = {
            'status': 'normal'
        }
        roles = yield self.role_model.find(condition).to_list(None)
        roles_data = [
            {
                'display_name': r['text'],
                'arg_name': r['name'],
                'checked': False
            } for r in roles
        ]
        raise gen.Return(roles_data)
