#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from behaviors import BuildItemData
import decimal
from errors import PermissionDeny
from behaviors import BuildShopItemData
import logging


class ItemDetail(RequestHandler):
    @LoginCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        if not 'ItemRead' in self.current_user['privileges']:
            raise PermissionDeny()

        type_id = self.get_argument('type_id', None)
        item_id = ObjectId(self.get_argument('id'))

        if type_id:
            if not 'ShopItemRead' in self.current_user['privileges']:
                raise PermissionDeny()
            category = yield self.category_model.find_one(
                { '_id': ObjectId(type_id) }
            )
            item = yield self.item_model.GetItemFromId(item_id)
            data = BuildShopItemData().BuildShopItemDeatil(item)
            data['shop_id'] = category['shop_id']
            data['type_id'] = category['_id']
            self.render('detail_page_item.html', data=data)
        else:
            if not 'ItemRead' in self.current_user['privileges']:
                raise PermissionDeny()
            item = yield self.item_repo_model.GetItemFromId(item_id)
            data = BuildItemData().BuildItemDeatil(item)
            self.render('detail_page_item.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        item_id = ObjectId(self.get_argument('id'))
        type = self.get_argument('type', None)
        name = self.get_argument('name', None)
        description = self.get_argument('des', None)
        status = self.get_argument('status', None)
        brand = self.get_argument('brand', None)
        note = self.get_argument('note', None)
        code = self.get_argument('code', None)
        price = self.get_argument('price', None)
        priority = self.get_argument('priority', None)
        is_special = self.get_argument('is_special', None)
        special_price = self.get_argument('special_price', None)
        limit = self.get_argument('limit', None)

        category_id = self.get_argument('type_id', None)

        if category_id:
            if not 'ShopItemUpdate' in self.current_user['privileges']:
                raise PermissionDeny()

            category = yield self.category_model.find_one(
                { '_id': ObjectId(category_id) }
            )
            new_item_data = {}
            new_item_data['shop_id'] = category['shop_id']
            new_item_data['category'] = category['_id']
            new_item_data['priority'] = 0
            if name:
                new_item_data['name'] = name.strip().encode('utf8')
            if price:
                new_item_data['price'] = int(decimal.Decimal(price)*100)
            if description:
                new_item_data['description'] = description.strip().encode('utf8')
            if priority:
                new_item_data['priority'] = int(priority.strip())
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

            result = yield self.item_model.update(
                { '_id': item_id },
                { '$set': new_item_data }
            )
            success = result['updatedExisting'] and result['ok'] == 1 and result['nModified'] > 0
            item = yield self.item_model.GetItemFromId(item_id)
            data = BuildShopItemData().BuildShopItemDeatil(item)
            data['shop_id'] = category['shop_id']
            data['type_id'] = category['_id']
            if success:
                data['flag'] = 'ok'
                data['message'] = '修改商品资料成功'
                self.render('detail_page_item.html', data=data)
            else:
                data['flag'] = 'error'
                data['message'] = '修改商品资料失败'
                self.render('detail_page_item.html', data=data)
        else:
            if not 'ItemUpdate' in self.current_user['privileges']:
                raise PermissionDeny()

            # Remove item from shop.
            if status in ['off', 'deleted', 'off_shelves']:
                item = yield self.item_repo_model.GetItemFromId(item_id)
                result = yield self.item_model.update(
                    { 'id': item['number'] },
                    { '$set': { 'status': 'off_shelves'} },
                    multi=True
                )

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
            #if code:
            #    new_item_data['number'] = int(code.strip())
            if price:
                new_item_data['price'] = int(decimal.Decimal(price.strip())*100)
            if priority:
                new_item_data['priority'] = float(decimal.Decimal(priority.strip()))

            if is_special == 'true':
                new_item_data['special_price'] = int(decimal.Decimal(special_price)*100)
                new_item_data['limit'] = int(limit)

            image_file = self.request.files.get('photo', '')
            if image_file:
                photo_bin = self.request.files['photo'][0]['body']
                image_id = yield self.image_model.Save(photo_bin)
                new_item_data['image_id'] = image_id

            result = yield self.item_repo_model.UpdateItem(item_id, new_item_data)
            success = result['updatedExisting'] and result['ok'] == 1 and result['nModified'] > 0
            item = yield self.item_repo_model.GetItemFromId(item_id)
            data = BuildItemData().BuildItemDeatil(item)
            if success:
                data['flag'] = 'ok'
                data['message'] = '修改商品资料成功'
            else:
                data['flag'] = 'error'
                data['message'] = '修改商品资料失败'
            self.render('detail_page_item.html', data=data)
