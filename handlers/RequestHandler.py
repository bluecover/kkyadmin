#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'zh'
__date__ = '3/19/15'


import base.RequestHandler
from pycket.session import SessionManager
import settings
from tornado import gen
from tornado.web import MissingArgumentError
import errors

class RequestHandler(base.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(RequestHandler, self).__init__(*args, **kwargs)
        self.session = SessionManager(self)

    def get_template_path(self):
        return settings.base.template_path

    @gen.coroutine
    def prepare(self):
        try:
            user_id = self.session.get(settings.redis.USER_KEY)
            if user_id:
                user = yield self.console_user_model.GetUserFromId(user_id)
                if user:
                    yield self.Login(user)
        except:
            pass

    def _handle_request_exception(self, error):
        if self._finished:
            return
        if isinstance(error, errors.Error):
            self.render_error(error)
        elif isinstance(error, MissingArgumentError):
            self.render_error(errors.ParamInvalidError(error.arg_name))
        else:
            super(RequestHandler, self)._handle_request_exception(error)

    def render_error(self, error):
        data = {
            'code': u'',
            'message': u'操作发生错误'
        }

        if isinstance(error, errors.PermissionDeny):
            data['code'] = error.error_code
            data['message'] = error.error_message

        self.render('global_error.html', data=data)

    @gen.coroutine
    def Login(self, user):
        if user['status'] in ['locked']:
            raise gen.Return(False)
        user['privileges'] = []
        roles = user['roles']
        for r in roles:
            role = yield self.role_model.GetRoleFromName(r)
            if role:
                privileges = role['privileges']
                user['privileges'].extend(privileges)

        self.session.set(settings.redis.USER_KEY, user['_id'])
        self.current_user = user
        raise gen.Return(True)
