#!/usr/bin/env python
# encoding=UTF8
__author__ = 'tinyproxy'
__date__ = '2014/10/16'

import logging

__all__ = ["ModelLoaderSingleton"]

class ModelLoaderSingleton(object):
    _cached = {}

    def __init__(self):
        super(ModelLoaderSingleton, self).__init__()

    def Use(self, name, args=None):
        # For mongodb
        if name not in ModelLoaderSingleton._cached:
            model_name = "models.%s"%name
            model = __import__(model_name)
            ModelLoaderSingleton._cached[name] = model.__dict__[name]
            if args is not None:
                ModelLoaderSingleton._cached[name].ProcessArguments(args)
        return ModelLoaderSingleton._cached[name]

    def Cache(self, name, value):
        # For redis
        if name in ModelLoaderSingleton._cached:
            return False
        else:
            ModelLoaderSingleton._cached[name] = value
            return True
