#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2/4/15'


SALTS = []
SALT_LENGTH = 3
candidates = '''`~!@#$%^&*()-_=+[{]};:,<.>/?\|'''
for c0 in candidates:
    for c1 in candidates:
        for c2 in candidates:
            SALTS.append(c0+c1+c2)
