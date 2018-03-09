#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2014/10/24'

from tornado import gen
from Behavior import Behavior
import logging
from SMSAPI import GetSMSAPI
from settings.switch import DEBUG

def _sendMessage(mobile, sm, **kwargs):
    GetSMSAPI(sm['SP']).SendMessage(mobile, sm, **kwargs)

class SendSM(Behavior):
    _REDIS_NAMESPACE = "__SM__"
    _MAX = 60
    _TTL = 3600
    def __init__(self):
        super(SendSM, self).__init__()

    @gen.coroutine
    def Action(self, mobile, sm, **kwargs):
        logging.info('in SendSM::Action')
        if DEBUG:
            logging.info("SKIP SEND SM ACTION IN DEBUG MODE")
            raise gen.Return(None)
        key = SendSM._REDIS_NAMESPACE+unicode(mobile).encode("UTF-8")

        logging.info('SMS key ' + str(key))

        yield gen.Task(
            self.async_redis.incr,
            key
        )

        value = yield gen.Task(
            self.async_redis.get,
            key
        )

        logging.info("SMS value " + str(value))

        value = int(value)
        if value < SendSM._MAX:
            yield gen.Task(
                self.async_redis.expire,
                key,
                SendSM._TTL
            )

            logging.info("SMS enqueue")

            self.queue.enqueue(
                _sendMessage,
                mobile,
                sm,
                **kwargs
            )
