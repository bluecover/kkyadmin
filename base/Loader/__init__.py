#!/usr/bin/env python
# encoding=UTF8
__author__ = 'tinyproxy'
__date__ = '2014/10/16'

__all__ = ["ModelLoaderSingleton"]

# When I wrote this framework, I was not sure if we will change loader's code,
# to avoid making lots of trouble, I decided to make the loader as a directory module,
# which provides more flexibility

from ModelLoaderSingleton import ModelLoaderSingleton