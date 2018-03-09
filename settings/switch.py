#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '22/01/15'
from settings import _configure as configure

DEBUG = True if configure.debug != 'false' else False
