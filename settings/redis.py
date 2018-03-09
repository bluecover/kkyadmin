#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2014/10/16'

from base import DEBUG

RQ_CACHE_KEY = "__ZEUS_RQ_QUEUE__"
DATA_CACHE_KEY = "__ZEUS_DATA_REDIS__"
SHARK_CACHE_KEY = "__ZEUS_SHARK_REDIS__"
WUKONG_CACHE_KEY = "__ZEUS_WUKONG_REDIS__"
__SESSION_MAX_CONNECTION__ = 62
__SESSION_EXPIRES_DAYS__ = 120
from settings import _configure
from settings import _configure as configure

# declare variables here to avoid gc
HOST = None
PORT = None
if configure.redis_server.find(':') < 0:
    HOST = configure.redis_server
    PORT = 6379
else:
    HOST, PORT = configure.redis_server.split(':')
    PORT = int(PORT)

PASSWORD = configure.redis_password
if not PASSWORD:
    PASSWORD = None

if DEBUG:
    RQ = 22
    DATA = 24
    SHARK_DATA = 9
    __SESSION_DB__ = 25
    __SESSION_NOTIFICATIONS__ = 26
else:
    RQ = 27
    DATA = 28
    SHARK_DATA = 13
    __SESSION_DB__ = 29
    __SESSION_NOTIFICATIONS__ = 30

# Session support

SESSION = {
    'engine': 'redis',
    'storage': {
        'host': HOST,
        'port': PORT,
        'password': PASSWORD,
        'db_sessions': __SESSION_DB__,
        'db_notifications': __SESSION_NOTIFICATIONS__,
        'max_connections': __SESSION_MAX_CONNECTION__
    },
    'cookies':{
        'expires_days':__SESSION_EXPIRES_DAYS__
    }
}

USER_KEY = '__ZEUS_USER_KEY__'
COOKIE_SECRET = "50c0e74b7ca7b61954de03632a55854a"

# Session support end
