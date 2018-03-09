#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/5/15'


SP = 'getui'
USER_APP = 'user'
COURIER_APP = 'courier'

PUSH_CONSOLE_SUBTASK_CANCEL = {
    'title': u'快快鱼',
    'content': u'您有一笔配送任务已取消',
    'transmission_content': {
        'type': 'task'
    }
}

PUSH_GODS_GIFT = {
    'title': u'快快鱼',
    'content': u'一个满3减2红包已发，请鱼丸笑纳~ 节日发红包是求爱，节日后继续发红包才是真爱！',
    'transmission_content': {
        'type': 'home'
    }
}

PUSH_GIVE_RED_PACKET = {
    'title': u'快快鱼',
    'content': u'你已获得满%s减%s元红包，马上打开快快鱼下单使用吧',
    'transmission_content': {
        'type': 'home'
    }
}
