#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'

from switch import DEBUG
from settings import _configure as configure
import os
import json

APP_ID = ""
APP_SECRET = ""


WUKONG_SERVER = configure.wukong_server

if DEBUG:
	APP_ID = "54d4e19b778d17046c86c8e6"
	APP_SECRET = "Zt5AzYQRt9XKrdo8LwOOZTy4iaun3T4c"
else:
	APP_ID = "54d4e19b778d17046c86c8e6"
	APP_SECRET = "Zt5AzYQRt9XKrdo8LwOOZTy4iaun3T4c"

ACCESS_TOKEN_URL = "%s/openapi.access.token.get" % WUKONG_SERVER
EXPRESS_NEW_URL = "%s/openapi.express.new" % WUKONG_SERVER
EXPRESS_STATUS_URL = "%s/openapi.express.status" % WUKONG_SERVER
EXPRESS_DONE_URL = '%s/openapi.express.done' % WUKONG_SERVER

LOG_INFO = '''
ACCESS_TOKEN_URL = %(ACCESS_TOKEN_URL)s
EXPRESS_NEW_URL = %(EXPRESS_NEW_URL)s
EXPRESS_STATUS_URL = %(EXPRESS_STATUS_URL)s
EXPRESS_DONE_URL = %(EXPRESS_DONE_URL)s
''' % {
	"ACCESS_TOKEN_URL": ACCESS_TOKEN_URL,
	"EXPRESS_NEW_URL": EXPRESS_NEW_URL,
	"EXPRESS_STATUS_URL": EXPRESS_STATUS_URL,
	"EXPRESS_DONE_URL": EXPRESS_DONE_URL
}

print LOG_INFO
