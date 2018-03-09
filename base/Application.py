#!/usr/bin/env python
# encoding=UTF8
__author__ = 'tinyproxy'
__date__ = '2014/10/16'

import tornado.web
import settings
from Loader import ModelLoaderSingleton
import tornadoredis
from redis import Redis
from rq import Queue
from third_party import orm
from HookFS import HookFS
from tornado import gen
import logging


class Application(tornado.web.Application):
    def __init__(self, *args, **kwargs):
        super(Application, self).__init__(*args, **kwargs)
        self._mongodb_connection = orm.Connection
        self._mongodb_connection.connect(host=settings.mongodb.MONGODB_URL, db_name=settings.mongodb.DATABASE)
        self._fs = self._mongodb_connection.get_fs(db_name=settings.mongodb.FS_DATABASE)
        self._loader = ModelLoaderSingleton()
        self._async_redis = tornadoredis.Client(
            host=settings.redis.HOST,
            port=settings.redis.PORT,
            password=settings.redis.PASSWORD,
            selected_db=settings.redis.DATA)
        self._async_redis.connect()
        self._shark_redis = tornadoredis.Client(
            host=settings.redis.HOST,
            port=settings.redis.PORT,
            password=settings.redis.PASSWORD,
            selected_db=settings.redis.SHARK_DATA)
        self._shark_redis.connect()
        self._wukong_redis = self._async_redis
        self._loader.Cache(settings.redis.DATA_CACHE_KEY, self._async_redis)
        self._loader.Cache(settings.redis.SHARK_CACHE_KEY, self._shark_redis)
        self._loader.Cache(settings.redis.WUKONG_CACHE_KEY, self._async_redis)
        self._rq_connection = Redis(db=settings.redis.RQ)
        self._rq_queue = Queue(connection=self._rq_connection)
        self._loader.Cache(settings.redis.RQ_CACHE_KEY, self._rq_queue)

        HookFS(self._fs)

    @staticmethod
    def _get_action(uri):
        index = uri.find('?')
        if index >= 0:
            return uri[1:index]
        else:
            return uri[1:]

    @gen.coroutine
    def log_request(self, handler):
        if handler.request.method == 'POST':
            if handler.get_status() < 400:
                try:
                    model = self._loader.Use('LogModel')
                    yield model.NewLog(
                        handler.current_user.get('_id', None),
                        self._get_action(handler.request.uri),
                        handler.get_status(),
                        handler.request.remote_ip,
                        handler.request.arguments
                    )
                except Exception as e:
                    logging.error(e)

        super(Application, self).log_request(handler)