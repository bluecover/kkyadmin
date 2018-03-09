#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '2/2/15'


from RequestHandler import RequestHandler
from errors import Error
from errors import ParamInvalidError
from errors import UnknownError
from tornado.web import MissingArgumentError
from third_party import superjson


class ApiRequestHandler(RequestHandler):
    SUPPORTED_METHODS = ["POST"]

    def render(self, data={}):
        retval = {
            "flag":"ok",
            "data":data
        }
        json_text = superjson.dumps(retval)
        self.write(json_text)
        self.finish()

    def initialize(self):
        super(RequestHandler, self).initialize()
        #Do not cache any content
        self.set_header('Cache-Control','no-cache, no-store, must-revalidate')#HTTP/1.1
        self.set_header('Pragma','no-cache')#HTTP/1.0
        self.set_header('Expires','0')#Proxies
        self.set_header("Content-Type", "application/json") # Set response content type

    def _handle_request_exception(self, error):
        if self._finished:
            return
        if isinstance(error, Error):
            self.render_error(error)
        elif isinstance(error, MissingArgumentError):
            self.render_error(ParamInvalidError(error.arg_name))
        else:
            super(RequestHandler, self)._handle_request_exception(error)

    def write_error(self, status_code, **kwargs):
        if status_code >= 500:
            self.render_error(UnknownError())
        else:
            super(RequestHandler, self).write_error(status_code, **kwargs)

    def render_error(self, error):
        if self._finished:
            return
        if isinstance(error, Error):
            result = {'flag': 'error', 'code': error.error_code}
            if hasattr(error, 'error_message'):
                result['reason'] = error.error_message
            else:
                result['reason'] = ''
        else:
            result = {'flag': 'error', 'reason': str(error)}
        self.write(superjson.dumps(result))
        self.finish()
