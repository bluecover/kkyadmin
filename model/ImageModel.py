#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '2015/01/23'


from third_party.orm import Document
from bson import ObjectId
from tornado import gen


class ImageModel(Document):
    _fs = None

    @staticmethod
    def SetFS(fs):
        ImageModel._fs = fs

    @classmethod
    @gen.coroutine
    def Get(cls, image_id):
        image_id = ObjectId(image_id)
        image = yield ImageModel._fs.get(image_id)
        image_content = yield image.read()
        raise gen.Return(image_content)

    @classmethod
    @gen.coroutine
    def Save(cls, image_binary):
        image_id = yield cls._fs.put(
            image_binary,
            type='image'
        )
        raise gen.Return(image_id)
