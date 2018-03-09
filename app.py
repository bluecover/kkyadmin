#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '22/01/15'

import settings
import logging
logging.basicConfig(level=settings.base.LOG_LEVEL, format=settings.base.LOG_FORMAT)

from base import Application
from tornado.ioloop import IOLoop
from urls import URLS


if __name__ == "__main__":
    app = Application(
        URLS,
        debug=True,
        pycket=settings.redis.SESSION,
        cookie_secret=settings.redis.COOKIE_SECRET
    )
    app.listen(settings.server.PORT)
    logging.info('Server is running on port %d'%settings.server.PORT)
    IOLoop.instance().start()
