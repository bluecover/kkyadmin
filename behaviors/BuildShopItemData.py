#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '4/21/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText


class BuildShopItemData(Behavior):
    @gen.coroutine
    def BuildShopItemList(self, shop_id, category_id):
        condition = {
            'shop_id': shop_id,
            'category': category_id,
            'old': {
                '$exists': False
            }
        }
        items = yield self.item_model.find(condition).sort([('priority', 1)]).to_list(None)
        data_items = []
        for i in items:
            image_id = i.get('image_id', None)
            if image_id:
                image_url = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(image_id) + '.jpg';
            else:
                image_url = ''
            data_items.append(
                {
                    'name': i['name'],
                    '_id': i['_id'],
                    'price': i['price']/100.0,
                    'img': image_url,
                    'status': ConvertText().ItemStatusToChinese(i['status']),
                    'priority': i['priority'],
                    'arg_name': i['_id'],
                    'status_color': ConvertText().ItemStatusColor(i['status'])
                }
            )
        data = {
            'shop_id': shop_id,
            'type_id': category_id,
            'items': data_items
        }
        raise gen.Return(data)


    def BuildShopItemDeatil(self, item):
        image_id = item.get('image_id', None)
        if image_id:
            image_url = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(image_id) + '.jpg';
        else:
            image_url = ''
        data = {
            'item': {
                'name': item['name'],
                '_id': item['_id'],
                'price': item['price']/100.0,
                'des': item.get('description', ''),
                'type': item['category'],
                'img': image_url,
                'brand': item.get('brand', ''),
                'createdTime': ConvertText().TimestampToText(item['created_time']),
                'status': ConvertText().ItemStatusToChinese(item['status']),
                'note': item.get('note', ''),
                'priority': item.get('priority', 0),
                'is_special': item.get('limit', 0) > 0,
                'special_price': item.get('special_price', 0),
                'limit': item.get('limit', 0)
            }
        }
        return data
