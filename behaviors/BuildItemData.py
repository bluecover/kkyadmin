#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/26/15'


from Behavior import Behavior
from tornado import gen
from ConvertText import ConvertText


class BuildItemData(Behavior):
    def BuildTableFrame(self, **kw):
        data = {
            'filters': {
                'types': {
                    'type': u'品类',
                    'name': u'名称',
                    'brand': u'品牌'
                },
                'status':{
                    'on': u'在售',
                    'off': u'下架',
                    'deleted': u'已删除',
                }
            },
            'extra_btns': [
                {
                    'text': u'添加商品',
                    'href': '/item_add'
                }
            ],
            'table_src': 'item_list'
        }
        return data

    @gen.coroutine
    def BuildTableContent(self, **kw):
        condition = {}
        if kw['filter_type'] == 'type':
            condition['category'] = kw['filter_value'].encode('utf8')
        if kw['filter_type'] == 'name':
            condition['name'] = kw['filter_value'].encode('utf8')
        if kw['filter_type'] == 'brand':
            condition['brand'] = kw['filter_value'].encode('utf8')
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

        query = self.item_repo_model.find(condition)
        items_count = yield query.count()
        items = yield query.limit(limit).skip(skip).to_list(None)

        datas = []
        for item in items:
            image_id = item.get('image_id', None)
            if image_id:
                image_url = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(image_id) + '.jpg';
            else:
                image_url = ''
            datas.append(
                [
                    {
                        'type': 'text',
                        'value': item['number']
                    },
                    {
                        'type': 'text',
                        'value': item['name']
                    },
                    {
                        'type': 'text',
                        'value': item['category']
                    },
                    {
                        'type': 'text',
                        'value': item['price']/100.0
                    },
                    {
                        'type': 'img',
                        'value': image_url
                    },
                    {
                        'type': 'status',
                        'value': ConvertText().ItemStatusToChinese(item['status']),
                        'color': ConvertText().ItemStatusColor(item['status'])
                    },
                    {
                        'type': 'button',
                        'value': u'查看',
                        'onclick': 'view("/item_detail?id=%s")' % str(item['_id'])
                    }
                ]
            )

        data = {
            'thead': [u'编号', u'名称', u'分类', u'价格', u'图片', u'状态', u'操作'],
            'datas': datas,
            'count': items_count
        }
        raise gen.Return(data)


    def BuildItemDeatil(self, item):
        image_id = item.get('image_id', None)
        if image_id:
            image_url = 'http://cdn.statics.kuaikuaiyu.com/image/' + str(image_id) + '.jpg';
        else:
            image_url = ''
        data = {
            'item': {
                'name': item['name'],
                '_id': item['_id'],
                'code': item['number'],
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
                'special_price': item.get('special_price', 0)/100.0,
                'limit': item.get('limit', 0)
            }
        }
        return data
