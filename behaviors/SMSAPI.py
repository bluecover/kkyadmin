#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'zhaohao'
__date__ = '2014/12/23'

from tornado.httpclient import HTTPClient
from urllib import urlencode
import logging
import datetime


class SMSAPI(object):
    def _GetSendUrl(self, smtype):
        pass
    def _CreateRequestBody(self, mobile, sm, **kw):
        pass
    def _DoRequest(self, url, data, callback):
        pass

    @staticmethod
    def _OnSendDone(response):
        logging.debug(response)
        logging.debug('Request is done!')
        pass

    def SendMessage(self, mobile, sm, **kw):
        send_url = self._GetSendUrl(sm['type'])
        post_data = self._CreateRequestBody(mobile, sm, **kw)
        self._DoRequest(send_url, post_data, callback=SMSAPI._OnSendDone)


class SMSAPI_YunPian(SMSAPI):
    API_URL = {
        'txt': 'http://yunpian.com/v1/sms/send.json',
        'tpl': 'http://yunpian.com/v1/sms/tpl_send.json'
    }
    API_KEY = '45ab6b415dd0d35a70224c377a19feea'
    SIGNATURE = '【快快鱼】'

    def _GetSendUrl(self, smtype):
        return SMSAPI_YunPian.API_URL[smtype]

    def _CreateRequestBody(self, mobile, sm, **kw):
        post_data = {
            'mobile': ','.join(mobile) if isinstance(mobile, list) else mobile,
            'apikey': SMSAPI_YunPian.API_KEY
        }
        dt = datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S")
        if sm['type'] == 'tpl':
            post_data['tpl_id'] = sm['tpl_id']
            if 'time' not in kw:
                kw['time'] = dt
            if kw['time'] == False:
                del kw['time']
            tpl_value = {}
            for k,v in kw.items():
                tpl_value['#' + k + '#'] = v
            post_data['tpl_value'] = urlencode(tpl_value)
        else: # smtype == 'txt'
            post_data['text'] = SMSAPI_YunPian.SIGNATURE\
                + sm['wording'] % kw + dt
        return post_data

    def _DoRequest(self, url, body, callback):
        body = urlencode(body)
        print body
        client = HTTPClient()
        response = client.fetch(
            url,
            body=body,
            method='POST',
            callback=callback
        )
        print response.body


class SMSAPI_Emay(SMSAPI):
    API_URL = {
        'txt': 'http://sdkhttp.eucp.b2m.cn/sdkproxy/sendsms.action',
        'tpl': 'http://sdkhttp.eucp.b2m.cn/sdkproxy/sendsms.action'
    }
    API_KEY = '3SDK-EMY-0130-JGVRP'
    PASSWORD = '052681'

    def _GetSendUrl(self, smtype):
        return SMSAPI_Emay.API_URL[smtype]

    def _CreateRequestBody(self, mobile, sm, **kw):
        post_data = {
            'cdkey': SMSAPI_Emay.API_KEY,
            'password': SMSAPI_Emay.PASSWORD,
            'phone': mobile,
            'message': sm['wording'] % kw
        }
        return post_data

    def _DoRequest(self, url, body, callback):
        body = urlencode(body)
        print body
        client = HTTPClient()
        response = client.fetch(
            url,
            method='POST',
            body=body,
            callback=callback
        )
        print response.body


class SMSAPI_Luosimao(SMSAPI):
    API_URL = {
        'txt': 'https://sms-api.luosimao.com/v1/send.json',
        'tpl': 'https://sms-api.luosimao.com/v1/send.json'
    }
    API_KEY = '9dd7faf47c8b4c4c0590b741f93be205'

    def _GetSendUrl(self, smtype):
        return SMSAPI_Luosimao.API_URL[smtype]

    def _CreateRequestBody(self, mobile, sm, **kw):
        post_data = {
            'mobile': mobile,
            'message': sm['wording'] % kw
        }
        return post_data

    def _DoRequest(self, url, body, callback):
        body = urlencode(body)
        print body
        client = HTTPClient()
        client.fetch(
            url,
            body=body,
            method='POST',
            auth_username='api',
            auth_password='key-%s' % SMSAPI_Luosimao.API_KEY,
            callback=callback
        )

SMSP = {
    'yunpian': SMSAPI_YunPian(),
    'emay': SMSAPI_Emay(),
    'luosimao': SMSAPI_Luosimao()
}

def GetSMSAPI(sp):
    return SMSP.get(sp, SMSP['yunpian'])
