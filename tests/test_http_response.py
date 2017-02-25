# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from w3lib.url import safe_url_string

from pycreeper.http.request import Request
from pycreeper.http.response import Response
from pycreeper.http.headers import Headers


class ResponseTest(unittest.TestCase):
    def test_init(self):
        self.assertRaises(Exception, Response)
        self.assertRaises(Exception, Response, url='http://www.example.com/')
        self.assertRaises(Exception, Response, request=Request('http://www.example.com/'))
        self.assertRaises(ValueError,
                          Response,
                          url='foo',
                          request=Request('http://www.example.com/')
                          )
        self.assertRaises(ValueError,
                          Response,
                          'http://www.example.com/',
                          status='foo',
                          request=Request('http://www.example.com/')
                          )
        self.assertRaises(TypeError,
                          Response,
                          'http://www.example.com/',
                          request='foo'
                          )
        response = Response('http://www.example.com/',
                            Request('http://www.example.com/')
                            )
        assert response.url
        assert not response.body
        response = Response('http://www.example.com/',
                            Request('http://www.example.com/'),
                            headers={'Content-Type': 'text/html',
                                     'Content-Length': 1234
                                     }
                            )
        self.assertIsInstance(response.headers, Headers)

    def test_copy(self):
        response1 = Response('http://www.example.com/',
                             headers={'Content-Type': 'text/html',
                                      'Content-Length': 1234
                                      },
                             request=Request('http://www.example.com/')
                             )
        response2 = response1.copy()
        assert response1.__dict__ == response2.__dict__
        self.assertEqual(response1.headers, response2.headers)
        self.assertEqual(response1.request, response2.request)
        self.assertEqual(response1, response2)

        self.assertIsNot(response1.headers, response2.headers)
        self.assertIsNot(response1.request, response2.request)
        self.assertIsNot(response1, response2)

    def test_url(self):
        response = Response('http://www.example.com/',
                            request=Request('http://www.example.com/')
                            )
        self.assertIsInstance(response.url, str)
        self.assertEqual(response.url, 'http://www.example.com/')
        response = Response(u'http://www.example.com?content=测试',
                            request=Request('http://www.example.com/')
                            )
        self.assertEqual(response.url,
                         safe_url_string('http://www.example.com?content=测试'))
        self.assertRaises(TypeError, Response, 123)

    def test_body(self):
        r1 = Response(url="http://www.example.com/",
                      request=Request('http://www.example.com/')
                      )
        assert r1.body == b''

        r2 = Response(url="http://www.example.com/",
                      body=b"",
                      request=Request('http://www.example.com/'))
        assert isinstance(r2.body, bytes)
        self.assertEqual(r2.encoding, 'utf-8')  # default encoding

        r3 = Response(url="http://www.example.com/",
                      body=u"Price: \xa3100",
                      encoding='utf-8',
                      request=Request('http://www.example.com/'))
        assert isinstance(r3.body, bytes)
        self.assertEqual(r3.body, b"Price: \xc2\xa3100")

        r4 = Response(url="http://www.example.com/",
                      request=Request('http://www.example.com/'),
                      body=u"Price: \xa3100",
                      encoding='latin1'
                      )
        assert isinstance(r4.body, bytes)
        self.assertEqual(r4.body, b"Price: \xa3100")

    def test_request(self):
        response = Response('http://www.example.com/',
                            request=Request('http://www.example.com/')
                            )
        self.assertIsInstance(response.request, Request)
        self.assertEqual(response.request, Request('http://www.example.com/'))
