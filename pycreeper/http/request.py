#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import six
from w3lib.url import safe_url_string

from headers import Headers


class Request(object):
    """ Request """

    def __init__(self, url, callback=None, method='GET', headers=None,
                 body=None, cookies=None, meta=None, encoding='utf-8',
                 dont_filter=False):
        self._encoding = encoding
        self.url = url
        self.body = body
        self.method = str(method).upper()
        self.callback = callback
        self.cookies = cookies or {}
        self.headers = Headers(headers or {}, encoding=encoding)
        self.dont_filter = dont_filter
        self._meta = dict(meta) if meta else {}

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
            if self._encoding is None:
                raise TypeError('Cannot convert unicode url - %s has no encoding' %
                                type(self).__name__)
            self._url = safe_url_string(url.encode(self._encoding))
        else:
            raise TypeError('Request url must be str or unicode, got %s:' % type(url).__name__)
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
            if self._encoding is None:
                raise TypeError('Cannot convert unicode body - %s has no encoding' %
                                type(self).__name__)
            self._body = body.encode(self._encoding)
        elif body is None:
            self._body = ''
        else:
            raise TypeError("Request body must either str or unicode. Got: '%s'" % type(body).__name__)

    @property
    def meta(self):
        return self._meta

    def copy(self, *args, **kwargs):
        """ copy """
        for key in ["encoding", "url", "method", "callback",
                    "headers", "body", "cookies", "meta", "dont_filter"]:
            kwargs.setdefault(key, getattr(self, key))
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def __str__(self):
        return "<%s %s>" % (self.method, self.url)

    __repr__ = __str__

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return self.__dict__ != other.__dict__
