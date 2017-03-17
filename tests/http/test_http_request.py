# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from w3lib.url import safe_url_string

from pycreeper.http.request import Request


class RequestTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(Exception, Request)
        self.assertRaises(ValueError, Request, 'foo')
        request = Request('http://www.example.com/')
        assert request.url
        assert not request.body
        request = Request('http://www.example.com/',
                          headers={'Content-Type': 'text/html',
                                   'Content-Length': 1234
                                   },
                          method='get'
                          )
        self.assertEqual(request.method, 'GET')

    def test_copy(self):
        request1 = Request('http://www.example.com/',
                           headers={'Content-Type': 'text/html',
                                    'Content-Length': 1234
                                    },
                           method='get'
                           )
        request2 = request1.copy()
        assert request1.__dict__ == request2.__dict__
        self.assertEqual(request1.headers, request2.headers)
        self.assertEqual(request1, request2)
        self.assertIsNot(request1, request2)

    def test_url(self):
        request = Request('http://www.example.com/')
        self.assertIsInstance(request.url, str)
        self.assertEqual(request.url, 'http://www.example.com/')
        request = Request(u'http://www.example.com?content=测试')
        self.assertEqual(request.url,
                         safe_url_string('http://www.example.com?content=测试'))
        self.assertRaises(TypeError, Request, 123)

    def test_body(self):
        r1 = Request(url="http://www.example.com/")
        assert r1.body == b''

        r2 = Request(url="http://www.example.com/", body=b"")
        assert isinstance(r2.body, bytes)
        self.assertEqual(r2.encoding, 'utf-8')  # default encoding

        r3 = Request(url="http://www.example.com/", body=u"Price: \xa3100", encoding='utf-8')
        assert isinstance(r3.body, bytes)
        self.assertEqual(r3.body, b"Price: \xc2\xa3100")

        r4 = Request(url="http://www.example.com/", body=u"Price: \xa3100", encoding='latin1')
        assert isinstance(r4.body, bytes)
        self.assertEqual(r4.body, b"Price: \xa3100")
