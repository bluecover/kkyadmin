#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/28/15'


from Behavior import Behavior
from tornado import gen


class RefundOrder(Behavior):
    @gen.coroutine
    def Action(self, order_id):
        order = yield self.order_model.GetOrderFromId(order_id)
        if not order['status'] in ['paid', 'sending', 'uncomment', 'done']:
            raise gen.Return(False)

        yield self.order_model.update(
            { '_id': order_id },
            {
                '$set': {
                    'status': 'refunded'
                }
            }
        )

        subtask_id = order['express_id']
        subtask = yield self.subtask_model.GetSubtaskFromId(subtask_id)
        yield self.subtask_model.update(
            { '_id': subtask_id },
            {
                '$set': {
                    'status': 'canceled'
                }
            }
        )

        task_id = subtask['owner_task']
        task = yield self.task_model.GetTaskFromId(task_id)
        canceled_subtasks_count = yield self.subtask_model.find(
            {
                '_id': { '$in': task['subtasks'] },
                'status': 'canceled'
            }
        ).count()
        if canceled_subtasks_count == len(task['subtasks']):
            yield self.task_model.update(
                { '_id': task_id },
                {
                    '$set': {
                        'status': 'canceled'
                    }
                }
            )
        else:
            done_subtasks_count = yield self.subtask_model.find(
                {
                    '_id': { '$in': task['subtasks'] },
                    'status': 'done'
                }
            ).count()
            if done_subtasks_count + canceled_subtasks_count == len(task['subtasks']):
                yield self.task_model.update(
                    { '_id': task_id },
                    {
                        '$set': {
                            'status': 'done'
                        }
                    }
                )

        raise gen.Return(True)
