#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/24/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
import json
from BuildAreaData import BuildAreaData
from BuildRoleData import BuildRoleData


class BuildUserData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kw['user'])
        data = {
            'filters': {
                'types': {
                        'name': u'帐号名',
                        'realname': u'真实姓名',
                        'mobile': u'手机号'
                },
                'status':{
                    'normal': u'正常',
                    'locked': u'锁定',
                }
            },
            'extra_btns': [
                {
                    'text': u'添加用户',
                    'href': '/member_add'
                }
            ],
            'table_src': 'member_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)

    @gen.coroutine
    def BuildTableContent(self, **kw):
        region = kw['area']
        if region == u'全部大区':
            region = None
        province = kw['province']
        if province == u'全部省份':
            province = None
        city = kw['city']
        if city == u'全部城市':
            city = None
        campus = kw['campus']
        if campus == u'全部校区':
            campus = None

        PAGE_SIZE = 20
        page = kw['page'] - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE

        other_condition = {}
        if kw['filter_type'] == 'name':
            other_condition['name'] = kw.get('filter_value')
        if kw['filter_type'] == 'realname':
            other_condition['realname'] = kw.get('filter_value')
        if kw['filter_type'] == 'mobile':
            other_condition['mobile'] = kw.get('filter_value')
        status = kw.get('filter_status', None)
        if status:
            other_condition['status'] = status

        users, users_count = yield self.console_user_model.GetUsersAndCountFromArea(
            skip,
            limit,
            region=region,
            province=province,
            city=city,
            school_name=campus,
            other_condition=other_condition
        )

        datas = []
        for u in users:
            roles_condition = {
                'name': {
                    '$in': u['roles']
                }
            }
            user_roles = yield self.role_model.find(roles_condition).to_list(None)
            user_roles_text_list = [r['text'] for r in user_roles]
            roles_text_str = '  '.join(user_roles_text_list)
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': u['name']
                    },
                    {
                        'type': 'text',
                        'value': u.get('realname', '')
                    },
                    {
                        'type': 'text',
                        'value': roles_text_str
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().UserStatusToChinese(u['status']),
                        'color': ConvertText().UserStatusColor(u['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/member_detail?id=%s")' % str(u['_id'])
                    }
                ]
            )
        data = {
            'thead': [u'登录名', u'真实姓名', u'角色', u'状态', u'操作'],
            'datas': datas,
            'count': users_count
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildUserDetail(self, current_user, detail_user):
        roles = yield BuildRoleData().BuildRoleCandidatesList()
        for r in roles:
            if r['arg_name'] in detail_user['roles']:
                r['checked'] = True
        area_full = yield BuildAreaData().BuildAreasWithSchools(current_user)
        data = {
            'member': {
                'name': detail_user['name'],
                'realname': detail_user.get('realname', ''),
                'status': ConvertText().UserStatusToChinese(detail_user['status']),
                '_id': detail_user['_id'],
                'mobile': detail_user.get('mobile', ''),
                'note': detail_user.get('note', '')
            },
            'roles': [
                {
                    'display_name': u'候选角色',
                    'sub_roles': roles
                }
            ],
            'areas': {
                'full': json.dumps(area_full),
                'choosed': json.dumps(
                    {
                        'area': detail_user.get('region', ''),
                        'province': detail_user.get('province', ''),
                        'city': detail_user.get('city', ''),
                        'campus': detail_user.get('school_name', '')
                    }
                )
            }
        }

        raise gen.Return(data)
