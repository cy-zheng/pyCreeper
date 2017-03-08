#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest
import requests
from pycreeper.http.cookies import CookieJar, potential_domain_matches
from pycreeper.http.request import Request
from pycreeper.http.response import Response
from pycreeper.downloader import DownloadHandler
from pycreeper.spider import Spider

HTTPBIN_URL = 'http://httpbin.org/'


class CookieJarTest(unittest.TestCase):

    def setUp(self):
        self.cookiejar = CookieJar()
        self.spider = Spider()
        self.downloader = DownloadHandler(spider=self.spider)

    def test_extract_cookies(self):
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1')
        response = self.downloader.fetch(request)
        self.cookiejar.extract_cookies(response, request)
        self.assertIn('key1', self.cookiejar._cookies['httpbin.org']['/'])

    def test_add_cookie_header(self):
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1')
        response = self.downloader.fetch(request)
        self.cookiejar.extract_cookies(response, request)
        request = Request(HTTPBIN_URL + '/cookies/set?key2=val2')
        self.cookiejar.add_cookie_header(request)
        response = self.downloader.fetch(request)
        self.cookiejar.extract_cookies(response, request)
        self.assertIn('key1', self.cookiejar._cookies['httpbin.org']['/'])
        self.assertIn('key2', self.cookiejar._cookies['httpbin.org']['/'])

    def test_make_cookie(self):
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1')
        response = self.downloader.fetch(request)
        self.assertEqual(self.cookiejar.make_cookies(response, request)[0].name, 'key1')
        self.assertEqual(self.cookiejar.make_cookies(response, request)[0].value, 'val1')


class PotentialDomainMatchesTest(unittest.TestCase):

    def test_basic(self):
        self.assertEqual(
            potential_domain_matches('abc.example.com'),
            ['abc.example.com', 'example.com', '.abc.example.com', '.example.com']
        )


if __name__ == "__main__":
    unittest.main()
