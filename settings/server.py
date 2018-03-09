#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '22/01/15'

from switch import DEBUG
from settings import _configure as configure


PORT = int(configure.server_port)
ADDRESS = configure.server_address
URL_PREFIX = configure.url_prefix
