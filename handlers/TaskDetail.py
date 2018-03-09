#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from behaviors import BuildTaskData


class TaskDetail(RequestHandler):
    RequiredPrivilege = 'TaskRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        task_id = ObjectId(self.get_argument('id'))
        data = yield BuildTaskData().BuildTaskDetail(task_id)
        if self.get_argument('task_forward', None):
            courier_id = ObjectId(self.get_argument('courier_id'))
            courier = yield self.courier_model.GetCourierFromId(courier_id)
            data['flag'] = 'ok'
            data['message'] = u'任务已转给：' + courier['name']
        self.render('detail_page_task.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        pass
    