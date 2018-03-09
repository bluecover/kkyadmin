#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '22/01/15'

__all__ = ['base', 'redis', 'server', 'switch', 'mongodb', 'sms', 'openapi', 'role',
           'item', 'bank', 'push']

import argparse
argument_parser = argparse.ArgumentParser()
argument_parser.add_argument('--debug', default='true')
argument_parser.add_argument('--mongodb-server', default="localhost:27017")
argument_parser.add_argument('--server-port', help='server port', default='20002')
argument_parser.add_argument('--server-address', help='server address', default='localhost')
argument_parser.add_argument('--url-prefix', help='server url prefix', default='http://localhost:20002')
argument_parser.add_argument('--wukong-server', help='wukong server', default='http://localhost:8999')
argument_parser.add_argument('--redis-server', default='localhost')
argument_parser.add_argument('--redis-password', default='')
_configure = argument_parser.parse_known_args()[0]

import switch
import server
import redis
import base
import mongodb
import sms
import role
import item
import bank
import push
