#!/usr/bin/env python
# -*- coding: utf-8 -*-

from RequestHandler import RequestHandler
from tornado import gen
from bson import ObjectId
from LoginCheck import LoginCheck
from PermissionCheck import PermissionCheck


class Gift(RequestHandler):
    RequiredPrivilege = 'CodeQuery'

    @LoginCheck
    @PermissionCheck
    @gen.coroutine
    def get(self, *args, **kwargs):
        data = {
            "system": {
                "menu":"客户服务",
                "submenu":"安慰红包",
                "content_src":"/helpdesk_gift_content",
            },
            "user": {
                "name": self.current_user["name"],
                "_id": self.current_user["_id"]
            }
        }
        self.render("index.html", data=data)