#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest
import json
from pycreeper.http.request import Request
from pycreeper.downloader import DownloadHandler
from pycreeper.spider import Spider
from pycreeper.downloader_middlewares.redirect_middlewares \
    import RedirectMiddleware

HTTPBIN_URL = 'http://httpbin.org'


class RedirectMiddlewaresTest(unittest.TestCase):

    def setUp(self):
        self.spider = Spider()
        self.spider.settings.set('TIMEOUT', 15)
        self.downloader = DownloadHandler(spider=self.spider)
        self.redirect_middlerwares = RedirectMiddleware(self.spider.settings,
                                                        self.spider.logger
                                                        )

    def test_process_response_relative_redirect(self):
        request = Request(
            HTTPBIN_URL + '/redirect/5',
        )
        response = self.downloader.fetch(request)
        response = self.redirect_middlerwares.process_response(request, response)
        self.assertIsInstance(response, Request)
        self.assertEqual(response.meta.get("redirect_count", 0), 1)
        self.assertEqual(response.url, 'http://httpbin.org/relative-redirect/4')

    def test_process_response_absolute_redirect(self):
        request = Request(
            HTTPBIN_URL + '/absolute-redirect/5',
        )
        response = self.downloader.fetch(request)
        response = self.redirect_middlerwares.process_response(request, response)
        self.assertIsInstance(response, Request)
        self.assertEqual(response.meta.get("redirect_count", 0), 1)
        self.assertEqual(response.url, 'http://httpbin.org/absolute-redirect/4')

    def test_max_redirect_count(self):
        redirect_count = 0
        request = Request(
            HTTPBIN_URL + '/redirect/15',
        )
        while True:
            response = self.downloader.fetch(request)
            response = self.redirect_middlerwares.process_response(request, response)
            request = response
            if not isinstance(request, Request):
                break
            redirect_count += 1
        self.assertEqual(redirect_count, 10)


if __name__ == "__main__":
    unittest.main()
