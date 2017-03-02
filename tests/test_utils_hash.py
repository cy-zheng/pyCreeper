#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from pycreeper.utils.hash import request_fingerprint
from pycreeper.http.request import Request

__doctests__ = ['pycreeper.utils.hash']

URLS = [
    'http://www.example.com/index.html#print',
    'http://www.example.com/index.html',
    'http://www.xxx.com/index.html?id=77&nameid=2905210001&page=1',
    'http://www.xxxxx.com/index.html?id=77&nameid=2905210001&page=1',
    'http://www.xxxxx.com/index.html?test123123',
    'http://www.xxxxx.com/index.html',
    'ftp://www.xxxxx.com/index.html'
]

REQUEST = [Request(url) for url in URLS]


class RequestFingerprintTest(unittest.TestCase):

    def test_basic(self):
        self.assertRaises(AttributeError, request_fingerprint, None)
        self.assertNotEqual(REQUEST[0], REQUEST[1])

    def test_not_equal(self):
        self.assertNotEqual(REQUEST[2], REQUEST[3])
        self.assertNotEqual(REQUEST[3], REQUEST[4])
        self.assertNotEqual(REQUEST[3], REQUEST[4])
        self.assertNotEqual(REQUEST[4], REQUEST[5])
        self.assertNotEqual(REQUEST[5], REQUEST[6])

if __name__ == "__main__":
    unittest.main()
