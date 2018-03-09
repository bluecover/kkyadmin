#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/20/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
from bson import ObjectId
from behaviors import ConvertText
from behaviors import BuildShopItemData


class ShopEditItemsOwn(RequestHandler):
    RequiredPrivilege = 'ShopUpdate'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('shop_id'))
        category_id = ObjectId(self.get_argument('type_id'))
        data = yield BuildShopItemData().BuildShopItemList(shop_id, category_id)
        insert_result = self.get_argument('result', None)
        if insert_result:
            if insert_result != 'None':
                item = yield self.item_model.find_one({'_id': ObjectId(insert_result)})
                data['flag'] = 'ok'
                data['message'] = u'添加商品成功：' + item.get('name', '')
            else:
                data['flag'] = 'error'
                data['message'] = '添加商品失败'
        self.render('detail_page_shop_edit_types_item_list.html', data=data)


    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        shop_id = ObjectId(self.get_argument('shop_id'))
        category_id = ObjectId(self.get_argument('type_id'))
        condition = {
            'shop_id': shop_id,
            'category': category_id,
            'old': {
                '$exists': False
            }
        }
        items = yield self.item_model.find(condition).to_list(None)
        deleted = []
        for i in items:
            arg_priority = str(i['_id'])
            priority = self.get_argument(arg_priority, None)
            if not priority:
                deleted.append(i['_id'])
                continue
            condition = {
                '_id': i['_id']
            }
            setter = {
                '$set': {}
            }
            if priority:
                setter['$set']['priority'] = int(priority)
            result = yield self.item_model.update(condition, setter)

        yield self.item_model.update(
            { '_id': { '$in': deleted } },
            { '$set': { 'status': 'deleted' } },
            multi=True
        )

        self.redirect('/shop_edit_items_types_item_list?shop_id=%s&type_id=%s' % (shop_id,category_id))
