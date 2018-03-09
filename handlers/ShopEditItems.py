#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/27/15'


from RequestHandler import RequestHandler
from tornado import gen
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck
import settings
from bson import ObjectId
from errors import PermissionDeny


class ShopEditItems(RequestHandler):
    RequiredPrivilege = 'ShopRead'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        shop_id = self.get_argument('id')
        shop = yield self.shop_model.GetShopFromId(ObjectId(shop_id))
        if shop['type'] in ['cvs']:
            data = {
                'shop': {
                    '_id': shop_id,
                },
                'types': [
                    {
                        '_id': catgory['id'],
                        'name': catgory['name']
                    } for catgory in settings.item.CATEGORIES
                ]
            }
            self.render('detail_page_shop_edit_items.html', data=data)
        else:
            data = {
                'shop_id': shop['_id'],
                'shop_name': shop.get('name', ''),
                'types': []
            }
            categories = yield self.category_model.GetCategoriesByShopId(ObjectId(shop_id))
            for c in categories:
                data['types'].append(
                    {
                        '_id': c['_id'],
                        'arg_name': c['_id'],
                        'name': c['name'],
                        'priority': c['priority']
                    }
                )

            self.render('detail_page_shop_edit_types.html', data=data)

    @LoginCheck
    @gen.coroutine
    def post(self, *args, **kwargs):
        if not 'ShopUpdate' in self.current_user['privileges']:
            raise PermissionDeny()

        shop_id = ObjectId(self.get_argument('id'))
        categories = yield self.category_model.GetCategoriesByShopId(shop_id)
        deleted = []
        for c in categories:
            arg_name = 'name_' + str(c['_id'])
            name = self.get_argument(arg_name, None)
            arg_priority = str(c['_id'])
            priority = self.get_argument(arg_priority, None)
            if not name and not priority:
                deleted.append(c['_id'])
                continue
            condition = { '_id': c['_id'] }
            setter = { '$set': {} }
            if name:
                setter['$set']['name'] = name
            if priority:
                setter['$set']['priority'] = int(priority)
            result = yield self.category_model.update(condition, setter)

        yield self.category_model.remove(
            { '_id': { '$in': deleted } }
        )
        yield self.item_model.remove(
            {
                'shop_id': shop_id,
                'category': { '$in': deleted }
            }
        )

        for k,v in self.request.arguments.items():
            if k.startswith('newnode_'):
                id = k[8:]
                name_key = 'name_newnode_' + id
                name = self.get_argument(name_key)
                priority = int(v[0])
                result = yield self.category_model.insert(
                    {
                        'shop_id': shop_id,
                        'name': name,
                        'priority': priority
                    }
                )

        self.redirect('/shop_edit_items?id=%s' % shop_id)
