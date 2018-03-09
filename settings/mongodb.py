#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '1/23/15'

from base import DEBUG
from settings import _configure as configure

USER = 'sa'
PASSWORD = 'kuaikuaiyu1219'
SERVER = configure.mongodb_server

if DEBUG:
    DATABASE = "shark-debug"
    SHARK_DB = "shark-debug"
    WUKONG_DB = "wukong-debug"
    CONSOLE_DB = "console"
else:
    DATABASE = "shark-release"
    SHARK_DB = "shark-release"
    WUKONG_DB = "wukong-release"
    CONSOLE_DB = "console-release"

FS_DATABASE = "kuaikuaiyu-fs"
MONGODB_URL = "mongodb://%s:%s@%s/admin"%(USER, PASSWORD, SERVER)

print MONGODB_URL
