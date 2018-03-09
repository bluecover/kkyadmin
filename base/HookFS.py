#!/usr/bin/env python
# encoding=UTF8
__author__ = 'tinyproxy'
__date__ = '2014/10/16'

from models import ImageModel

def HookFS(fs):
    ImageModel.SetFS(fs)
