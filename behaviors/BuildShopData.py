#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/27/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText
from BuildAreaData import BuildAreaData
import json
import decimal
import datetime
from Utils import Utils


class BuildShopData(Behavior):
    @gen.coroutine
    def BuildTableFrame(self, **kw):
        areas_with_schools = yield BuildAreaData().BuildAreasWithSchools(kw['user'])
        data = {
            'filters': {
                'types': {
                    'type': u'类型',
                    'campus': u'归属校区'
                },
                'status':{
                    'open': u'营业中',
                    'closed': u'休息中',
                    'out': u'已关闭'
                }
            },
            'extra_btns': [
                {
                    'text': u'添加店铺',
                    'href': '/shop_add'
                }
            ],
            'table_src': 'shop_list',
            'area_full': json.dumps(areas_with_schools)
        }
        raise gen.Return(data)

    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'type':
            condition['type'] = kw['filter_value'].encode('utf8')
        status = kw.get('filter_status', None)
        if status:
            condition['status'] = status
        if kw['filter_time_start']:
            condition['created_time'] = { '$gte': kw['filter_time_start'] }
        if kw['filter_time_end']:
            condition_time = condition.setdefault('created_time', {})
            condition_time['$lte'] = kw['filter_time_end']

        PAGE_SIZE = 20
        page = kw['page'] - 1
        skip = page * PAGE_SIZE
        limit = PAGE_SIZE

        shops, shops_count = yield self.FindShopsByArea(
            skip=skip,
            limit=limit,
            region=kw['area'],
            province=kw['province'],
            city=kw['city'],
            school=kw['campus'],
            extra_condition=condition
        )

        datas = []
        for shop in shops:
            school_name = ''
            school_of_shop = yield self.school_model.GetSchoolFromId(shop['school_district'])
            if school_of_shop:
                school_name = school_of_shop['name']
            status = shop['status']
            is_working = self.IsShopWorking(shop)
            if status == 'open' and is_working == False:
                status = 'closed'
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': shop['name']
                    },
                    {
                        'type': 'text',
                        'value': shop['mobile']
                    },
                    {
                        'type': 'text',
                        'value': school_name
                    },
                    {
                        'type': 'text',
                        'value': ConvertText().TimestampToText(shop['created_time'])
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().ShopStatusToChinese(status),
                        'color': ConvertText().ShopStatusColor(self.GetShopStatus(shop))
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/shop_detail?id=%s")' % str(shop['_id'])
                    }
                ]
            )

        data = {
            'thead': [u'姓名', u'手机', u'校区', u'时间', u'状态', u'操作'],
            'datas': datas,
            'count': shops_count
        }
        raise gen.Return(data)


    @gen.coroutine
    def BuildShopDeatil(self, shop):
        school_of_shop = yield self.school_model.GetSchoolFromId(shop['school_district'])
        if not school_of_shop:
            school_of_shop = {}

        open_time = shop.get('open_hour', [0,0])
        open_hour_start = open_time[0] / 3600
        open_minute_start = (open_time[0] % 3600) / 60
        open_hour_end = open_time[1] / 3600
        open_minute_end = (open_time[1] % 3600) / 60
        work_hour = [
            open_hour_start,
            open_minute_start,
            open_hour_end,
            open_minute_end
        ]

        data = {
            'name': shop.get('name', ''),
            'mobile': shop.get('mobile', ''),
            '_id': shop.get('_id', ''),
            'type': ConvertText().ShopTypeToChinese(shop.get('type', '')),
            'address': shop.get('address', ''),
            'area': school_of_shop.get('region', ''),
            'province': school_of_shop.get('province', ''),
            'city': school_of_shop.get('city', ''),
            'campus': school_of_shop.get('name', ''),
            'position': shop.get('location', [0,0]),
            'work_hour': work_hour,
            'delivery_fee': shop.get('delivery_price', 0) / 100.0,
            'min_delivery_amount': shop.get('min_cost_to_deliver', 0) / 100.0,
            'createdTime': ConvertText().TimestampToText(shop.get('created_time', 0)),
            'status': ConvertText().ShopStatusToChinese(self.GetShopStatus(shop)),
            'note': shop.get('description', ''),
            'notice': shop.get('bulletin_message', '')
        }

        raise gen.Return(data)

    @gen.coroutine
    def BuildShopFromRequest(self, req):
        shop_data = {}

        name = req.get_argument('name', u'未命名')
        if name:
            shop_data['name'] = name.encode('utf8')

        type = req.get_argument('type', None)
        if type:
            shop_data['type'] = type

        mobile = req.get_argument('mobile', '')
        shop_data['mobile'] = mobile.encode('utf8')

        status = req.get_argument('status', 'open')
        shop_data['status'] = status

        address = req.get_argument('address', '')
        shop_data['address'] = address.encode('utf8')

        min_cost_to_deliver = req.get_argument('min_delivery_price', '0')
        shop_data['min_cost_to_deliver'] = int(decimal.Decimal(min_cost_to_deliver.strip())*100)

        delivery_price = req.get_argument('delivery_price', '0')
        shop_data['delivery_price'] = int(decimal.Decimal(delivery_price.strip())*100)

        if type != 'cvs':
            shop_data['delivery_price'] = 100
        
        if type != 'express':
            shop_data['delivery_price'] = 0

        note = req.get_argument('note', '')
        shop_data['description'] = note.encode('utf8')

        notice = req.get_argument('notice', '')
        shop_data['bulletin_message'] = notice.encode('utf8')

        lng = req.get_argument('lng', 0.0)
        lat = req.get_argument('lat', 0.0)
        shop_data['location'] = [float(lng), float(lat)]

        shop_data['region'] = req.get_argument('area').encode('utf8')
        shop_data['province'] = req.get_argument('province').encode('utf8')
        shop_data['city'] = req.get_argument('city').encode('utf8')
        shop_data['school_name'] = req.get_argument('campus').encode('utf8')

        start_hour = req.get_argument('work_hour_start_hour', 0)
        start_minute = req.get_argument('work_hour_start_minutes', 0)
        end_hour = req.get_argument('work_hour_end_hour', 0)
        end_minute = req.get_argument('work_hour_end_minutes', 0)
        if not start_hour:
            start_hour = 0
        if not start_minute:
            start_minute = 0
        if not end_hour:
            end_hour = 0
        if not end_minute:
            end_minute = 0
        open_hour = [
            int(start_hour) * 3600 + int(start_minute) * 60,
            int(end_hour) * 3600 + int(end_minute) * 60
        ]
        shop_data['open_hour'] = open_hour

        school = yield req.school_model.GetSchoolFromName(shop_data['school_name'])
        shop_data['school_district'] = school['_id']

        raise gen.Return(shop_data)

    @gen.coroutine
    def BuildShopItems(self, shop_id, category_name):
        category_condition = {
            'shop_id': shop_id,
            'name': category_name
        }

        category = yield self.category_model.find_one(category_condition)
        if category:
            on_sale_items_condition = {
                'shop_id': shop_id,
                'category': category['_id'],
                'status': 'on_sale',
                'old': { '$exists': False }
            }
            on_sale_items = yield self.item_model.find(on_sale_items_condition).to_list(None)
        else:
            on_sale_items = []

        on_sale_item_numbers = [ _['id'] for _ in on_sale_items ]
        on_sale_item_prices = { _['id']:_['price'] for _ in on_sale_items }
        on_sale_item_descriptions = { _['id']:_.get('description', '') for _ in on_sale_items }

        repo_item_condition = {
            'category': category_name,
            'status': 'on'
        }
        sort_condition = [
            ('priority', -1),
        ]
        repo_items = yield self.item_repo_model.find(repo_item_condition).sort(sort_condition).to_list(None)

        items_data = []
        for ri in repo_items:
            item_data = {
                '_id': ri['_id'],
                'code': ri['number'],
                'name': ri['name'],
                'choosed': True if ri['number'] in on_sale_item_numbers else False
            }

            if ri['number'] in on_sale_item_numbers:
                price = on_sale_item_prices[ri['number']] / 100.0
                description = on_sale_item_descriptions[ri['number']]
            else:
                price = ri['price'] / 100.0
                description = ri.get('description', '')
            item_data['price'] = price
            item_data['description'] = description

            image_id = ri.get('image_id', None)
            if image_id:
                item_data['img'] = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(image_id) + '.jpg'
            else:
                item_data['img'] = ''
            items_data.append(item_data)
        raise gen.Return(items_data)


    @gen.coroutine
    def FindShopsByArea(self, skip=None, limit=None, region=None, province=None, city=None, school=None,
                        extra_condition={}):
        school_condition = yield Utils().BuildSchoolCondition(region, province, city, school, school_key='school_district')
        shop_condition = dict(school_condition.items() + extra_condition.items())
        query = self.shop_model.find(shop_condition)
        shops_count = yield query.count()
        if skip is not None and limit is not None:
            shops = yield query.limit(limit).skip(skip).to_list(None)
        else:
            shops = yield query.to_list(None)

        raise gen.Return((shops, shops_count))


    def IsShopWorking(self, shop):
        now = datetime.datetime.now()
        seconds_in_day = now.hour*3600 + now.minute*60 + now.second
        open_start = shop['open_hour'][0]
        open_end = shop['open_hour'][1]
        if open_start > open_end:
            open_end += 24*3600
        if shop['status'] == 'open' and open_start < seconds_in_day < open_end:
            return True
        else:
            return False


    def GetShopStatus(self, shop):
        status = shop['status']
        is_working = self.IsShopWorking(shop)
        if status == 'open' and is_working == False:
            status = 'closed'
        return status
