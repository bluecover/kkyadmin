#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'tinyproxy'
__date__ = '25/01/15'

from hashlib import sha1


class HashAuthTokens(object):
    def __init__(self):
        super(HashAuthTokens, self).__init__()

    def Action(self, tokens):
        tokens.sort()
        token_hash = sha1(''.join(tokens)).hexdigest()
        return token_hash

