# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest
import time
import json

from pycreeper.utils.exceptions import TimeoutException
import gevent

from gevent.pool import Pool
from pycreeper.downloader_middlewares.cookies_middlewares import CookiesMiddleware
from pycreeper.downloader import DownloadHandler
from pycreeper.spider import Spider
from pycreeper.http.request import Request
from pycreeper.http.response import Response
from selenium import webdriver
from gevent.lock import BoundedSemaphore

HTTPBIN_URL = 'http://httpbin.org'




class DownloadHandlerTest(unittest.TestCase):
    def setUp(self):
        self.spider = Spider()
        self.spider.settings.set('TIMEOUT', 15)
        self.driver = None
        self.driver_sem = BoundedSemaphore(1)

    def test_concurrency_with_delayed_url(self):
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        n = 5
        pool = Pool(n)
        urls = []
        for i in range(n):
            urls.append(HTTPBIN_URL + '/delay/1')
        time_start = time.time()
        pool.map(dh.fetch, [Request(url) for url in urls])
        time_total = time.time() - time_start
        self.assertLess(time_total, n)

    def test_timeout_static(self):
        self.spider.settings.set('TIMEOUT', 5)
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        self.assertRaises(TimeoutException, dh.fetch, Request(HTTPBIN_URL + '/delay/10'))

    def test_timeout_dynamic(self):
        self.driver = webdriver.PhantomJS()
        self.spider.settings.set('TIMEOUT', 5)
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        self.assertRaises(TimeoutException, dh.fetch, Request(HTTPBIN_URL + '/delay/10', dynamic=True))
        self.driver.close()

    def test_post_data_static(self):
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST'))
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status, 200)

    def test_post_data_content_static(self):
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body={'text': 'pycreeper'}))
        self.assertIsInstance(response, Response)
        self.assertEqual(json.loads(response.body)['form'], {'text': 'pycreeper'})

        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body=u'Unicode测试'))
        self.assertEqual(json.loads(response.body)['data'], 'Unicode测试')

        response = dh.fetch(Request(HTTPBIN_URL + '/post', method='POST', body='中文测试'))
        self.assertEqual(json.loads(response.body)['data'], '中文测试')
        self.assertEqual(response.status, 200)

    def test_get_data(self):
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        response = dh.fetch(Request(HTTPBIN_URL + '/get'))
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status, 200)

    def test_dynamic_request(self):
        self.driver = webdriver.PhantomJS()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        request = Request(HTTPBIN_URL + '/get', dynamic=True)
        dh.fetch(request)
        self.driver.close()

    def test_dynamic_request_wait(self):
        self.driver = webdriver.PhantomJS()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        request = Request(HTTPBIN_URL + '/get', dynamic=True, wait=3)
        dh.fetch(request)
        self.driver.close()

    def test_dynamic_request_timeout(self):
        self.driver = webdriver.PhantomJS()
        self.spider.settings.set('TIMEOUT', 5)
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        request = Request(HTTPBIN_URL + '/delay/10', dynamic=True)
        self.assertRaises(TimeoutException, dh.fetch, request)
        self.driver.close()

    def test_dynamic_request_concurrency(self):
        self.driver = webdriver.PhantomJS()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        n = 5
        pool = Pool(n)
        urls = []
        for i in range(n):
            urls.append(HTTPBIN_URL + '/delay/1')
        time1 = time.time()
        pool.map(dh.fetch, [Request(url, dynamic=True, wait=5) for url in urls])
        self.assertGreater(time.time() - time1, n)
        self.driver.close()

    def test_dynamic_request_cookie_between_static_and_dynamic(self):
        cm = CookiesMiddleware(self.spider, self.spider.settings)
        self.driver = webdriver.PhantomJS()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1&key2=val2',
                          dynamic=True, meta={'cookiejar': 'test'})
        response = dh.fetch(request)
        cm.process_response(request, response)
        request = Request(HTTPBIN_URL + '/cookies', meta={'cookiejar': 'test'})
        cm.process_request(request)
        response = dh.fetch(request)
        self.assertEqual(json.loads(response.body)['cookies'],
                         {u'key1': u'val1', u'key2': u'val2'})
        self.driver.close()

    def test_dynamic_request_multi_cookiejar(self):
        cm = CookiesMiddleware(self.spider, self.spider.settings)
        self.driver = webdriver.PhantomJS()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)

        # jar 1
        request = Request(HTTPBIN_URL + '/cookies/set?key1=val1',
                          dynamic=True, meta={'cookiejar': 'test1'})
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)

        # jar 2
        request = Request(HTTPBIN_URL + '/cookies/set?key2=val2',
                          dynamic=True, meta={'cookiejar': 'test2'})
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)

        # test jar2
        request = Request(HTTPBIN_URL + '/cookies', meta={'cookiejar': 'test2'})
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)
        self.assertEqual(json.loads(response.body)['cookies'], {u'key2': u'val2'})

        # test jar1
        request = Request(HTTPBIN_URL + '/cookies', meta={'cookiejar': 'test1'})
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)
        self.assertEqual(json.loads(response.body)['cookies'], {u'key1': u'val1'})
        self.driver.close()

    def test_dynamic_request_browser_actions(self):
        cm = CookiesMiddleware(self.spider, self.spider.settings)
        self.driver = webdriver.Chrome()
        dh = DownloadHandler(self.spider, self.driver, self.driver_sem)

        def _actions(driver):
            driver.find_element_by_name('account').send_keys("username")
            driver.find_element_by_name('password').send_keys("pwd")
            driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[2]/button').click()
            gevent.sleep(5)

        request = Request('https://www.zhihu.com/#signin',
                          dynamic=True, meta={'cookiejar': 'test'},
                          browser_actions=[_actions],
                          )
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)

        request = Request('https://www.zhihu.com', dynamic=True, meta={'cookiejar': 'test'})
        cm.process_request(request)
        response = dh.fetch(request)
        cm.process_response(request, response)
        print response.body
        self.driver.close()


class DownloadTest(unittest.TestCase):
    pass


if __name__ == "__main__":
    unittest.main()
