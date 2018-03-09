#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '5/21/15'

from pymongo import MongoClient
from bson import ObjectId
import pickle
import datetime
import time
import sys
import logging

client = MongoClient('mongodb://sa:kuaikuaiyu1219@123.56.131.68:7900/admin')

db_console = client['console-release']
db_shark = client['shark-release']
db_wukong = client['wukong-release']
c_order = db_shark['order']
c_school = db_wukong['schools']
c_order_statistics = db_console['order_statistics']
c_user_statistics = db_console['user_statistics']
c_region = db_console['regions']
c_user = db_shark['user']


def create_school_order_statistics(school, date):
    start_date_str = date.strftime('%Y%m%d')

    start_time = int(time.mktime(date.timetuple()) * 1000)
    end_time = start_time + 24*60*60*1000

    school_orders = list(c_order.find(
        {
            'school_id': school['_id'],
            'created_time': {
                '$gte': start_time,
                '$lt': end_time
            }
        }
    ))
    logging.info('school order count: ' + str(len(school_orders)))

    order_statistic = {
        'date': start_date_str,
        'school_id': school['_id'],
        'school_name': school['name'],
        'region': school['region'],
        'province': school['province'],
        'city': school['city'],
        'unpaid': 0,
        'cancel': 0,
        'paid': 0,
        'sending': 0,
        'uncomment': 0,
        'done': 0,
        'refunded': 0,
        'item_price': 0,
        'delivery_price': 0,
        'discount_price': 0
    }

    for order in school_orders:
        order_statistic[order['status']] += 1
        order_statistic['item_price'] += order['items_price']
        order_statistic['delivery_price'] += order['delivery_price']
        order_statistic['discount_price'] += order['discount_price']

    result = c_order_statistics.update(
        {
            'date': start_date_str,
            'school_id': school['_id']
        },
        {
            '$set': order_statistic
        },
        upsert=True
    )

    return order_statistic


def create_region_order_statistics(school_order_statistics, date):
    city_statistics = {}
    province_statistics = {}
    region_statistics = {}

    total_statistics = {
        'date': date.strftime('%Y%m%d'),
        'school_name': u'全部校区',
        'region': u'全部大区',
        'province': u'全部省份',
        'city': u'全部城市',
        'unpaid': 0,
        'cancel': 0,
        'paid': 0,
        'sending': 0,
        'uncomment': 0,
        'done': 0,
        'refunded': 0,
        'item_price': 0,
        'delivery_price': 0,
        'discount_price': 0
    }

    def _add_to_stat(total, single):
        total['unpaid'] += single['unpaid']
        total['cancel'] += single['cancel']
        total['paid'] += single['paid']
        total['sending'] += single['sending']
        total['uncomment'] += single['uncomment']
        total['done'] += single['done']
        total['refunded'] += single['refunded']
        total['item_price'] += single['item_price']
        total['delivery_price'] += single['delivery_price']
        total['discount_price'] += single['discount_price']

    for sos in school_order_statistics:
        _add_to_stat(total_statistics, sos)

        # CITY
        city_stat = city_statistics.setdefault(
            sos['city'],
            {
                'date': sos['date'],
                'school_name': u'全部校区',
                'region': sos['region'],
                'province': sos['province'],
                'city': sos['city'],
                'unpaid': 0,
                'cancel': 0,
                'paid': 0,
                'sending': 0,
                'uncomment': 0,
                'done': 0,
                'refunded': 0,
                'item_price': 0,
                'delivery_price': 0,
                'discount_price': 0
            }
        )
        _add_to_stat(city_stat, sos)

        # PROVINCE
        province_stat = province_statistics.setdefault(
            sos['province'],
            {
                'date': sos['date'],
                'school_name': u'全部校区',
                'region': sos['region'],
                'province': sos['province'],
                'city': u'全部城市',
                'unpaid': 0,
                'cancel': 0,
                'paid': 0,
                'sending': 0,
                'uncomment': 0,
                'done': 0,
                'refunded': 0,
                'item_price': 0,
                'delivery_price': 0,
                'discount_price': 0
            }
        )
        _add_to_stat(province_stat, sos)

        # REGION
        region_stat = region_statistics.setdefault(
            sos['region'],
            {
                'date': sos['date'],
                'school_name': u'全部校区',
                'region': sos['region'],
                'province': u'全部省份',
                'city': u'全部城市',
                'unpaid': 0,
                'cancel': 0,
                'paid': 0,
                'sending': 0,
                'uncomment': 0,
                'done': 0,
                'refunded': 0,
                'item_price': 0,
                'delivery_price': 0,
                'discount_price': 0
            }
        )
        _add_to_stat(region_stat, sos)

    for k,v in city_statistics.items():
        result = c_order_statistics.insert(v)
    for k,v in province_statistics.items():
        result = c_order_statistics.insert(v)
    for k,v in region_statistics.items():
        result = c_order_statistics.insert(v)

    result = c_order_statistics.insert(total_statistics)


def get_user_device_token(user):
    if not user or not 'device_token' in user:
        return None
    device_token = user['device_token'].get('android')
    if not device_token:
        device_token = user['device_token'].get('ios')
    return device_token


def create_order_statistics_of_date(date):
    start_time = int(time.mktime(date.timetuple()) * 1000)
    end_time = start_time + 24*60*60*1000
    logging.info(datetime.datetime.fromtimestamp(start_time/1000))

    schools = list(c_school.find({}))
    logging.info('school count: ' + str(len(schools)))

    school_order_statistics = []
    for school in schools:
        school_order_statistics.append(
            create_school_order_statistics(school, date)
        )

    create_region_order_statistics(school_order_statistics, date)


def create_region_user_statistics(school_user_statistics, date):
    city_statistics = {}
    province_statistics = {}
    region_statistics = {}

    total_statistics = {
        'date': date.strftime('%Y%m%d'),
        'school_name': u'全部校区',
        'region': u'全部大区',
        'province': u'全部省份',
        'city': u'全部城市',
        'new_users': 0,
        'total_users': 0
    }

    def _add_to_stat(total, single):
        total['new_users'] += single['new_users']
        total['total_users'] += single['total_users']

    for sus in school_user_statistics:
        _add_to_stat(total_statistics, sus)

        # CITY
        city_stat = city_statistics.setdefault(
            sus['city'],
            {
                'date': sus['date'],
                'school_name': u'全部校区',
                'region': sus['region'],
                'province': sus['province'],
                'city': sus['city'],
                'new_users': 0,
                'total_users': 0
            }
        )
        _add_to_stat(city_stat, sus)

        # PROVINCE
        province_stat = province_statistics.setdefault(
            sus['province'],
            {
                'date': sus['date'],
                'school_name': u'全部校区',
                'region': sus['region'],
                'province': sus['province'],
                'city': u'全部城市',
                'new_users': 0,
                'total_users': 0
            }
        )
        _add_to_stat(province_stat, sus)

        # REGION
        region_stat = region_statistics.setdefault(
            sus['region'],
            {
                'date': sus['date'],
                'school_name': u'全部校区',
                'region': sus['region'],
                'province': u'全部省份',
                'city': u'全部城市',
                'new_users': 0,
                'total_users': 0
            }
        )
        _add_to_stat(region_stat, sus)

    for k,v in city_statistics.items():
        result = c_user_statistics.insert(v)
    for k,v in province_statistics.items():
        result = c_user_statistics.insert(v)
    for k,v in region_statistics.items():
        result = c_user_statistics.insert(v)

    result = c_user_statistics.insert(total_statistics)

def create_school_user_statistics(school, date):
    start_date_str = date.strftime('%Y%m%d')
    start_time = int(time.mktime(date.timetuple()) * 1000)
    end_time = start_time + 24*60*60*1000

    user_statistic = {
        'date': start_date_str,
        'school_id': school['_id'],
        'school_name': school['name'],
        'region': school['region'],
        'province': school['province'],
        'city': school['city'],
        'new_users': 0,
        'total_users': 0
    }

    user_ids = c_order.find(
        {
            'school_id': school['_id'],
            'created_time': { '$lt': end_time }
        }
    ).distinct('user_id')

    found_device_tokens = {}
    total_users_count = 0
    new_users_count = 0

    for user_id in user_ids:
        try:
            most_early_order = c_order.find(
                {
                    'user_id': user_id,
                    'created_time': { '$lt': end_time }
                }
            ).sort([('created_time',1)])[0]

            user = c_user.find_one({'_id': user_id})
            device_token = get_user_device_token(user)
            if device_token and not device_token in found_device_tokens:
                found_device_tokens[device_token] = 1
                total_users_count += 1
                order_time = most_early_order['created_time']
                if order_time >= start_time and order_time < end_time:
                    new_users_count += 1

        except:
            continue

    user_statistic['total_users'] = total_users_count
    user_statistic['new_users'] = new_users_count

    result = c_user_statistics.insert(user_statistic)

    return user_statistic


def create_user_statistics_of_date(date):
    start_time = int(time.mktime(date.timetuple()) * 1000)
    end_time = start_time + 24*60*60*1000
    logging.info(datetime.datetime.fromtimestamp(start_time/1000))

    schools = list(c_school.find({}))
    school_user_statistics = []
    for school in schools:
        school_user_statistics.append(
            create_school_user_statistics(school, date)
        )

    create_region_user_statistics(school_user_statistics, date)


if __name__ == '__main__':
    if len(sys.argv) < 4:
        current_datetime = datetime.datetime.now()
        start_date = datetime.datetime(current_datetime.year, current_datetime.month, current_datetime.day)
        start_date -= datetime.timedelta(days=1)
        day_count = 1
        target = 'order'
    else:
        start_date = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
        day_count = int(sys.argv[2])
        target = sys.argv[3]

    for i in range(0, day_count):
        if target in ['all', 'order']:
            create_order_statistics_of_date(start_date)
        if target in ['all', 'user']:
            create_user_statistics_of_date(start_date)
        start_date -= datetime.timedelta(days=1)
