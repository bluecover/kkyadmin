#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/31/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
import time
from behaviors import SendSM
import logging
from settings import sms


class TaskForward(RequestHandler):
    RequiredPrivilege = 'TaskTransfer'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        param_id = self.get_argument('id', None)
        task_id = ObjectId(param_id)
        task = yield self.task_model.GetTaskFromId(task_id)
        school_couriers = yield self.courier_model.GetCouriersFromDistrictId(task['district_id'])
        school_courier_ids = [c['_id'] for c in school_couriers]
        available_schedules = yield self.schedule_model.GetAvailableCourierSchedules(
            school_courier_ids,
            int(time.time())
        )
        available_courier_ids = [sched['courier'] for sched in available_schedules]

        data_couriers = []
        for courier in school_couriers:
            if courier['_id'] in available_courier_ids:
                data_couriers.append(
                    {
                        '_id': courier['_id'],
                        'mobile': courier['mobile'],
                        'name': courier['name']
                    }
                )

        data = {
            'couriers': data_couriers,
            'task_id': task_id
        }
        self.render('task_forward.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        task_id = ObjectId(self.get_argument('t_id'))
        courier_id = ObjectId(self.get_argument('c_id'))
        task = yield self.task_model.GetTaskFromId(task_id)

        subtask_condition = {
            '_id': {
                '$in': task['subtasks']
            }
        }
        all_subtasks_can_schedule = True
        subtasks = yield self.subtask_model.find(subtask_condition).to_list(None)
        for subtask in subtasks:
            if subtask['status'] in ['delivering', 'confirmed', 'done', 'lock_for_confirm']:
                all_subtasks_can_schedule = False
                break

        if all_subtasks_can_schedule and task['status'] in ['waiting', 'dispatched']:
            courier = yield self.courier_model.GetCourierFromId(courier_id)
            condition = {
                '_id': task_id
            }
            updater = {
                '$set': {
                    'status': 'dispatched',
                    'dispatched_time': int(time.time()*1000),
                    'courier_id': courier['_id'],
                    'courier_name': courier['name'],
                    'courier_mobile': courier['mobile']
                }
            }
            result = yield self.task_model.update(condition, updater)
            if result['updatedExisting'] and result['ok'] == 1:
                subtask_condition = {
                    '_id': {
                        '$in': task['subtasks']
                    }
                }
                subtask_updater = {
                    '$set': {
                        'status': 'dispatched',
                        'dispatched_time': int(time.time()*1000)
                    }
                }
                yield self.subtask_model.update(subtask_condition, subtask_updater, multi=True)

                # set order sending
                order_ids = [ObjectId(t['express_no']) for t in subtasks]
                yield self.order_model.update(
                    { '_id': { '$in': order_ids } },
                    {
                        '$set': {
                            'status': 'sending',
                            'courier_id': courier['_id'],
                            'courier_name': courier['name'],
                            'courier_mobile': courier['mobile']
                        }
                    },
                    multi=True
                )

                sms_args = {}
                logging.info('[TaskForward] sms send to: ' + str(courier['mobile']))
                yield SendSM().Action(courier['mobile'], sms.SMS_NEW_TASK_NOTIFICATION, **sms_args)

                self.redirect('/task_detail?id=%s&task_forward=1&courier_id=%s' % (str(task_id),courier['_id']))
            else:
                data = {
                    'task_id': task_id,
                    'flag': 'error',
                    'message': '转单失败'
                }
                self.render('task_forward.html', data=data)
        else:
            data = {
                'task_id': task_id,
                'flag': 'error',
                'message': '转单失败：该状态下任务不可转'
            }
            self.render('task_forward.html', data=data)
