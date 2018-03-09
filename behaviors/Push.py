#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/5/15'


from push import PushNotification
from Behavior import Behavior
import settings
import uuid
import json
import copy


class Push(Behavior):
    def Action(self, app_name, device_token, push_msg, **kw):
        kw_args = self._GeneratePushArgs(push_msg, **kw)

        if 'android' in device_token:
            self.queue.enqueue(
                PushNotification,
                settings.push.SP,
                app_name,
                'notification',
                [device_token['android']],
                **kw_args
            )

        if 'ios' in device_token:
            self.queue.enqueue(
                PushNotification,
                settings.push.SP,
                app_name,
                'transmission',
                [device_token['ios']],
                **kw_args
            )


    def _GeneratePushArgs(self, push_msg, **kw):
        msg = copy.deepcopy(push_msg)
        transmission_content = msg['transmission_content']
        transmission_content['id'] = str(uuid.uuid4())
        for k,v in kw.items():
            if k == 'content':
                msg['content'] = v
            elif k == 'content_args':
                msg['content'] = msg['content'] % v
            else:
                transmission_content[k] = v
        transmission_content_str = json.dumps(transmission_content)
        msg['transmission_content'] = transmission_content_str
        return msg
