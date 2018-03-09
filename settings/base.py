#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '22/01/15'

import logging
from switch import DEBUG
APP_NAME = "CONSOLE"

LOG_FORMAT = "[%(levelname)s, %(asctime)s, %(pathname)s:%(lineno)d] %(message)s"
LOG_LEVEL = logging.INFO
if DEBUG:
    LOG_LEVEL = logging.DEBUG

if DEBUG:
    template_path = "/home/www/panel_plus/dev"
else:
    template_path = "/home/www/panel_plus/release"
