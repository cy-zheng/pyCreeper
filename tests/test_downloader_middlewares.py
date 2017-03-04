# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from pycreeper.downloader_middlewares import DownloaderMiddlewareManager
from pycreeper.downloader_middlewares.middlewares import UserAgentMiddleware, RetryMiddleware
from pycreeper.spider import Spider
from pycreeper.http.request import Request
from pycreeper.http.response import Response


class RetryMiddlewareTest(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()

    def test_basic(self):
        self.assertRaises(AttributeError, RetryMiddleware,
                          self.spider.settings, None)

    def test_process_response(self):
        request = Request('http://httpbin.org/')
        response = Response('http://httpbin.org/', request, status=500)
        rm = RetryMiddleware(self.spider.settings, self.spider.logger)
        request.meta["dont_retry"] = True
        self.assertEqual(rm.process_response(request, response), response)

        request.meta["dont_retry"] = False
        request = rm.process_response(request, response)
        self.assertIsInstance(request, Request)
        self.assertEqual(request.meta.get("retry_count"), 1)
        request = rm.process_response(request, response)
        self.assertIsInstance(request, Request)
        request = rm.process_response(request, response)
        self.assertIsInstance(request, Request)
        self.assertIsInstance(rm.process_response(request, response), Response)


class UserAgentMiddlewareTest(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()

    def test_basic(self):
        self.assertRaises(AttributeError, UserAgentMiddleware,
                          self.spider.settings, None)

    def test_process_request(self):
        request = Request('http://httpbin.org/')
        self.assertIs(request.headers.get("User-Agent"), None)
        uam = UserAgentMiddleware(self.spider.settings, self.spider.logger)
        uam.process_request(request)
        self.assertIsInstance(request.headers.get("User-Agent"), str)


class DownloaderMiddlewareManagerTest(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()
        self.spider.settings.set('DOWNLOADER_MIDDLEWARES',
                                 {
                                     'pycreeper.downloader_middlewares.middlewares.UserAgentMiddleware': 100,
                                     'pycreeper.downloader_middlewares.middlewares.RetryMiddleware': 200,
                                 })

    def test_methods(self):
        dmm = DownloaderMiddlewareManager(self.spider)
        rm = RetryMiddleware(self.spider.settings, self.spider.logger)
        uam = UserAgentMiddleware(self.spider.settings, self.spider.logger)
        process_request = [uam.process_request]
        process_response = [rm.process_response]
        process_exception = [rm.process_exception]
        self.assertEqual(len(dmm.methods['process_request']), len(process_request))
        for i in range(len(process_request)):
            self.assertEqual(dmm.methods['process_request'][i].__name__, process_request[i].__name__)

        self.assertEqual(len(dmm.methods['process_response']), len(process_response))
        for i in range(len(process_response)):
            self.assertEqual(dmm.methods['process_response'][i].__name__, process_response[i].__name__)

        self.assertEqual(len(dmm.methods['process_exception']), len(process_exception))
        for i in range(len(process_exception)):
            self.assertEqual(dmm.methods['process_exception'][i].__name__, process_exception[i].__name__)


if __name__ == "__main__":
    unittest.main()
