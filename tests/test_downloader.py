# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest
import time
import json

from requests.exceptions import ReadTimeout

from requests import Session

from gevent.pool import Pool

from pycreeper.downloader import DownloadHandler
from pycreeper.spider import Spider
from pycreeper.http.request import Request
from pycreeper.http.response import Response

HTTPBIN_URL = 'http://httpbin.org/'


class DownloadHandlerTest(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()

    def test_concurrency_with_delayed_url(self):
        dh = DownloadHandler(self.spider)
        n = 5
        pool = Pool(n)
        urls = []
        for i in range(n):
            urls.append(HTTPBIN_URL + '/delay/1')
        time_start = time.time()
        pool.map(dh.fetch, [Request(url) for url in urls])
        time_total = time.time() - time_start
        self.assertLess(time_total, n)

    def test_timeout(self):
        self.spider.settings.set('TIMEOUT', 5)
        dh = DownloadHandler(self.spider)
        self.assertRaises(ReadTimeout, dh.fetch, Request(HTTPBIN_URL + '/delay/10'))

    def test_post_data(self):
        dh = DownloadHandler(self.spider)
        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST'))
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status, 200)

    def test_post_data_content(self):
        dh = DownloadHandler(self.spider)
        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body={'text': 'pycreeper'}))
        self.assertIsInstance(response, Response)
        self.assertEqual(json.loads(response.body)['form'], {'text': 'pycreeper'})

        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body=u'Unicode测试'))
        self.assertEqual(json.loads(response.body)['data'], 'Unicode测试')

        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body='中文测试'))
        self.assertEqual(json.loads(response.body)['data'], '中文测试')
        self.assertEqual(response.status, 200)

    def test_get_data(self):
        dh = DownloadHandler(self.spider)
        response = dh.fetch(Request(HTTPBIN_URL + '/get'))
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status, 200)


class DownloadTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
