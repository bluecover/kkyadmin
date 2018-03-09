#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/27/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from bson import ObjectId
import settings
import re
import decimal
from behaviors import BuildShopData
from errors import PermissionDeny
import logging


class ShopEditItemsContent(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'ShopRead' in self.current_user['privileges']:
            raise PermissionDeny()

        shop_id = ObjectId(self.get_argument('shop_id'))
        faked_category_id = self.get_argument('id', None)
        if not faked_category_id or faked_category_id == '0':
            self.write('')
            raise gen.Return(None)
        faked_category = settings.item.GetCategoryFromId(faked_category_id)
        if not faked_category:
            self.write('')
            raise gen.Return(None)

        data_items = yield BuildShopData().BuildShopItems(shop_id, faked_category['name'])

        data = {
            'items': data_items,
            'shop_id': shop_id
        }
        self.render('detail_page_shop_edit_items_content.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'ShopUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        shop_id = ObjectId(self.get_argument('shop_id'))
        faked_category_id = self.get_argument('id')
        hardcoded_category = settings.item.GetCategoryFromId(faked_category_id)

        selected_items = {}
        for k,v in self.request.arguments.items():
            m = re.findall('.*_(.*)_checked', k)
            if m:
                selected_items[m[0]] = {}
        for k,v in self.request.arguments.items():
            m = re.findall('.*_(.*)_price', k)
            if m and m[0] in selected_items:
                selected_items[m[0]]['price'] = int(decimal.Decimal(v[0])*100)

        condition = {
            'shop_id': shop_id,
            'name': hardcoded_category['name']
        }
        category = yield self.category_model.find_one(condition)
        if not category and selected_items:
            category_data = {
                'shop_id': shop_id,
                'name': hardcoded_category['name'],
                'priority': hardcoded_category['priority']
            }
            new_category_id = yield self.category_model.insert(category_data)
            category = yield self.category_model.find_one({'_id': new_category_id})

        condition = {
            '_id': {  '$in': [ObjectId(_) for _ in selected_items] }
        }
        selected_repo_items = yield self.item_repo_model.find(condition).to_list(None)
        selected_item_numbers = [_['number'] for _ in selected_repo_items]

        condition = {
            'category': hardcoded_category['name']
        }
        all_repo_items = yield self.item_repo_model.find(condition).to_list(None)
        all_repo_item_numbers = [_['number'] for _ in all_repo_items]

        on_sale_items_condition = {
            'shop_id': shop_id,
            'category': category['_id'],
            'status': 'on_sale',
            'old': { '$exists': False }
        }
        current_shop_on_sale_items = yield self.item_model.find(on_sale_items_condition).to_list(None)
        go_off_shelves_item_numbers = [
            i['id']
            for i in current_shop_on_sale_items
                if i ['id'] in all_repo_item_numbers and not i['id'] in selected_item_numbers
        ]

        condition = {
            'shop_id': shop_id,
            'category': category['_id'],
            'old': { '$exists': False },
            'id': { '$in': go_off_shelves_item_numbers }
        }
        updater = {
            '$set': { 'status': 'off_shelves' }
        }
        result = yield self.item_model.update(condition, updater, multi=True)
        logging.info('[ShopEditItemsContent] ' + self.current_user.get('name','') + ' off_shelves: ' + str(go_off_shelves_item_numbers))

        # current_shop_on_sale_item_numbers = [_['id'] for _ in current_shop_on_sale_items]
        for item in selected_repo_items:
            condition = {
                'shop_id': shop_id,
                'category': category['_id'],
                'id': item['number'],
                'name': item['name']
            }
            updater = {
                '$set': {
                    'status': 'on_sale',
                    'price': selected_items[str(item['_id'])]['price'],
                    'priority': item['priority'],
                    'image_id': item['image_id'],
                    'description': item.get('description', '')
                }
            }

            if 'limit' in item:
                updater['$set']['special_price'] = item['special_price']
                updater['$set']['limit'] = item['limit']

            result = yield self.item_model.update(condition, updater, upsert=True)

        data_items = yield BuildShopData().BuildShopItems(shop_id, category['name'])
        data = {
            'items': data_items,
            'shop_id': shop_id,
            'flag': 'ok',
            'message': u'修改成功'
        }
        self.render('detail_page_shop_edit_items_content.html', data=data)
