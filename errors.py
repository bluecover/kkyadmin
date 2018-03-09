# -*- coding:utf-8 -*-
# author = 'paul'
# date = '2015-01-23 10:57:51'


class Error(Exception):
    def __init__(self, error_code):
        self.error_code = error_code


class UnknownError(Error):
    def __init__(self):
        super(UnknownError, self).__init__('0000')


class ParamInvalidError(Error):
    def __init__(self, invalid_param=None):
        super(ParamInvalidError, self).__init__('0001')
        if invalid_param is not None:
            self.error_message = 'Invalid param: %s' % invalid_param


class AuthExpire(Error):
    def __init__(self):
        super(AuthExpire, self).__init__('10')
        self.error_message = u'授权信息超时，请重新登录'


class AccountInvalid(Error):
    def __init__(self):
        super(AccountInvalid, self).__init__('11')
        self.error_message = u'手机或密码错误，请重新输入'


class PermissionDeny(Error):
    def __init__(self):
        super(PermissionDeny, self).__init__('20')
        self.error_message = u'操作非法'


class OldVersion(Error):
    def __init__(self):
        super(OldVersion, self).__init__('30')
        self.error_message = u'客户端版本过旧，请及时更新'


class VerifyCodeInvalid(Error):
    def __init__(self):
        super(VerifyCodeInvalid, self).__init__('40')
        self.error_message = u'验证码非法'

class NotHaveEnoughMoney(Error):
    def __init__(self):
        super(NotHaveEnoughMoney, self).__init__('50')
        self.error_message = u'账户余额不足'


class AccountNotExist(Error):
    def __init__(self):
        super(AccountNotExist, self).__init__('60')
        self.error_message = u'账户不存在'


class AccountExist(Error):
    def __init__(self):
        super(AccountExist, self).__init__('70')
        self.error_message = u'账户已注册'


class InvalidMasterKey(Error):
    def __init__(self):
        super(InvalidMasterKey, self).__init__('10000')
        self.error_message = "Invalid master key"

class DuplicateError(Error):
    def __init__(self, key, value):
        super(DuplicateError, self).__init__('11000')
        self.error_message = "duplicate key %s value %s"%(key, value)

class InvalidAppIdOrAppSecret(Error):
    def __init__(self):
        super(InvalidAppIdOrAppSecret, self).__init__('12000')
        self.error_message = "invalid app ID or app secret"

class InvalidAccessToken(Error):
    def __init__(self):
        super(InvalidAccessToken, self).__init__('13000')
        self.error_message = "invalid access token"
