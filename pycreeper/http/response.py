# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Response Object """

import six
from w3lib.url import safe_url_string
from pycreeper.http.request import Request


class Response(object):
    """ Response """

    def __init__(self, url, request, status=200, cookiejar=None,
                 body='', encoding='utf-8'):
        self._encoding = encoding
        self.url = url
        self.status = int(status)
        self.cookiejar = cookiejar
        self.body = body
        self.request = request

    @property
    def encoding(self):
        return self._encoding

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        if isinstance(url, str):
            self._url = safe_url_string(url)
        elif isinstance(url, six.text_type):
            if self.encoding is None:
                raise TypeError('Cannot convert unicode url - %s has no encoding' %
                                type(self).__name__)
            self._url = safe_url_string(url.encode(self.encoding))
        else:
            raise TypeError('Response url must be str or unicode, got %s:' % type(url).__name__)
        if ':' not in self._url:
            raise ValueError('Missing scheme in request url: %s' % self._url)

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, body):
        if isinstance(body, str):
            self._body = body
        elif isinstance(body, six.text_type):
            if self.encoding is None:
                raise TypeError('Cannot convert unicode body - %s has no encoding' %
                                type(self).__name__)
            self._body = body.encode(self.encoding)
        elif body is None:
            self._body = ''
        else:
            raise TypeError("Response body must either str or unicode. Got: '%s'" % type(body).__name__)

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, value):
        if isinstance(value, Request):
            self._request = value.copy()
        else:
            raise TypeError("Response request must be pycreeper.Request. Got: '%s'" % type(value).__name__)

    def copy(self, *args, **kwargs):
        """ copy """
        for key in ["url", "status", "cookiejar", "body", "request", "encoding"]:
            kwargs.setdefault(key, getattr(self, key))

        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def __str__(self):
        return "<%d %s>" % (self.status, self.url)

    __repr__ = __str__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__
