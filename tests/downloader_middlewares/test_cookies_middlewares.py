# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'


import unittest
import requests
import json
from pycreeper.http.cookies import CookieJar, potential_domain_matches
from pycreeper.http.request import Request
from pycreeper.http.response import Response
from pycreeper.downloader import DownloadHandler
from pycreeper.spider import Spider
from pycreeper.downloader_middlewares.middlewares import CookiesMiddleware

HTTPBIN_URL = 'http://httpbin.org'


class CookieMiddlewaresTest(unittest.TestCase):

    def setUp(self):
        self.cookiejar = CookieJar()
        self.spider = Spider()
        self.spider.settings.set('TIMEOUT', 15)
        self.downloader = DownloadHandler(spider=self.spider)
        self.cookie_middlerwares = CookiesMiddleware(self.spider.settings,
                                                     self.spider.logger
                                                     )

    def test_process_request_dont_merge_cookies(self):
        request = Request(
            HTTPBIN_URL + '/cookies',
            meta={
                'dont_merge_cookies': True
            },
            cookies={
                'key1': 'val1',
                'key2': 123
            }
        )
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'], {})

    def test_process_request_set_cookie(self):
        request = Request(
            HTTPBIN_URL + '/cookies',
            meta={
                'cookiejar': 'test'
            },
            cookies={
                'key1': 'val1',
                'key2': 'val2'
            }
        )
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'],
                         {
                             "key1": "val1",
                             "key2": 'val2',
                         })

    def test_process_request_set_cookie_without_cookiejar(self):
        request = Request(
            HTTPBIN_URL + '/cookies',
            cookies={
                'key1': 'val1',
                'key2': 'val2'
            }
        )
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        request = Request(
            HTTPBIN_URL + '/cookies',
        )
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'], {})

    def test_process_request_set_cookie_between_request(self):
        request = Request(
            HTTPBIN_URL + '/cookies',
            meta={
                'cookiejar': 'test'
            },
            cookies={
                'key1': 'val1',
            }
        )
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'],
                         {
                             "key1": "val1",
                         })

        request = Request(
            HTTPBIN_URL + '/cookies',
            meta={
                'cookiejar': 'test'
            },
            cookies={
                'key2': 'val2',
            }
        )
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'],
                         {
                             "key1": "val1",
                             "key2": "val2"
                         })

    def test_process_response(self):
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1',
                          meta={"cookiejar": "test"})
        response = self.downloader.fetch(request)
        self.cookie_middlerwares.process_response(request, response)
        request = Request(HTTPBIN_URL + '/cookies',
                          meta={"cookiejar": "test"})
        self.cookie_middlerwares.process_request(request)
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'],
                         {
                             "key1": "val1",
                         })

    def test_process_response_without_cookiejar(self):
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1')
        response = self.downloader.fetch(request)
        self.cookie_middlerwares.process_response(request, response)
        request = Request(HTTPBIN_URL + '/cookies')
        response = self.downloader.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'], {})

if __name__ == "__main__":
    unittest.main()
