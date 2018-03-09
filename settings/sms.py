#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2014/10/24'


TEMPLATE_IDS = {
    'yunpian': {
        'NEW_TASK_NOTIFICATION': '704933',
        'RED_PACKET': '762417'
    },
    'emay': {},  # DO NOT supoort yet.
    'luosimao': {}  # DO NOT supoort yet.
}

SP = 'yunpian'
SP_TPL_ID = TEMPLATE_IDS[SP]

SMS_NEW_TASK_NOTIFICATION = {
    'SP': SP,
    'type': 'tpl',
    'tpl_id': SP_TPL_ID['NEW_TASK_NOTIFICATION'],
    'wording': ''
}

SMS_RED_PACKET = {
    'SP': SP,
    'type': 'tpl',
    'tpl_id': SP_TPL_ID['RED_PACKET'],
    'wording': ''
}
