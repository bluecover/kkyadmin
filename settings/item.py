#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/27/15'


CATEGORIES = [
    { 'name': u'套餐', 'id': 'cat_0', 'priority': 1 },
    { 'name': u'饮料', 'id': 'cat_1', 'priority': 2 },
    { 'name': u'零食', 'id': 'cat_2', 'priority': 3 },
    { 'name': u'速食', 'id': 'cat_3', 'priority': 4 },
    { 'name': u'乳品', 'id': 'cat_4', 'priority': 5 },
    { 'name': u'酒水', 'id': 'cat_5', 'priority': 6 },
    { 'name': u'日用', 'id': 'cat_6', 'priority': 7 }
]

def GetCategoryFromId(id):
    cat = filter(lambda x: x['id'] == id, CATEGORIES)
    if cat:
        return cat[0]
    else:
        return None
