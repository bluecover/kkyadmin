#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
import decimal
from behaviors import BuildItemData
from PermissionCheck import PermissionCheck
import time
from bson import ObjectId
import logging


class ItemCreate(RequestHandler):
    RequiredPrivilege = 'ItemCreate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {}
        category_id = self.get_argument('type_id', None)
        if category_id:
            category = yield self.category_model.find_one(
                { '_id': ObjectId(category_id) }
            )
            data['type_id'] = category['_id']
            data['shop_id'] = category['shop_id']
        self.render('detail_page_item.html', data=data)

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        type = self.get_argument('type', None)
        name = self.get_argument('name', None)
        description = self.get_argument('des', None)
        status = self.get_argument('status', None)
        brand = self.get_argument('brand', None)
        note = self.get_argument('note', None)
        code = self.get_argument('code', None)
        price = self.get_argument('price', None)
        priority = self.get_argument('priority', None)
        category_id = self.get_argument('type_id', None)
        is_special = self.get_argument('is_special', None)
        special_price = self.get_argument('special_price', None)
        limit = self.get_argument('limit', None)

        if category_id:

            category = yield self.category_model.find_one(
                { '_id': ObjectId(category_id) }
            )
            new_item_data = {}
            new_item_data['shop_id'] = category['shop_id']
            new_item_data['category'] = category['_id']
            new_item_data['created_time'] = int(time.time()*1000)
            new_item_data['priority'] = 0

            missing_data = False

            if name:
                new_item_data['name'] = name.strip().encode('utf8')
            if price:
                new_item_data['price'] = int(decimal.Decimal(price)*100)
            if description:
                new_item_data['description'] = description.strip().encode('utf8')
            if status:
                if status == 'on':
                    new_item_data['status'] = 'on_sale'
                elif status == 'off':
                    new_item_data['status'] = 'off_shelves'
                elif status == 'deleted':
                    new_item_data['status'] = 'deleted'
            #if brand:
            #    new_item_data['brand'] = brand.strip().encode('utf8')
            image_file = self.request.files.get('photo', '')
            if image_file:
                photo_bin = self.request.files['photo'][0]['body']
                image_id = yield self.image_model.Save(photo_bin)
                new_item_data['image_id'] = image_id

            if not name or not price or not status or not image_file:
                data = {
                    'flag': 'error',
                    'message': u'添加商品失败'
                }
                self.render('detail_page_item.html', data=data)
                raise gen.Return(None)

            result = yield self.item_model.insert(new_item_data)
            self.redirect('/shop_edit_items_types_item_list?shop_id=%s&type_id=%s&result=%s'
                          % (category['shop_id'], category_id, result))

        else:

            new_item_data = {}
            if type:
                new_item_data['category'] = type.strip().encode('utf8')
            if name:
                new_item_data['name'] = name.strip().encode('utf8')
            if description:
                new_item_data['description'] = description.strip().encode('utf8')
            if brand:
                new_item_data['brand'] = brand.strip().encode('utf8')
            if note:
                new_item_data['note'] = note.strip().encode('utf8')
            if status:
                new_item_data['status'] = status
            if code:
                new_item_data['number'] = int(code.strip())
            if price:
                new_item_data['price'] = int(decimal.Decimal(price)*100)
            if priority:
                new_item_data['priority'] = float(decimal.Decimal(priority.strip()))

            new_item_data['created_time'] = int(time.time()*1000)

            image_file = self.request.files.get('photo', '')
            if image_file:
                photo_bin = self.request.files['photo'][0]['body']
                image_id = yield self.image_model.Save(photo_bin)
                new_item_data['image_id'] = image_id

            if is_special == 'true':
                new_item_data['special_price'] = int(decimal.Decimal(special_price)*100)
                new_item_data['limit'] = int(limit)

            data = {
                'flag': 'error',
                'message': u'添加商品失败'
            }

            try:
                result = yield self.item_repo_model.InsertItem(new_item_data)
                if result:
                    item = yield self.item_repo_model.GetItemFromId(result)
                    data = BuildItemData().BuildItemDeatil(item)
                    data['flag'] = 'ok'
                    data['message'] = '添加商品成功'
                else:
                    data = {
                        'flag': 'error',
                        'message': u'添加商品失败'
                    }
            except:
                pass

            self.render('detail_page_item.html', data=data)
