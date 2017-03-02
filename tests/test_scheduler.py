#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from pycreeper.scheduler import RequestFilter, Scheduler
from pycreeper.http.request import Request
from pycreeper.utils.log import get_logger
from pycreeper.conf.settings import Settings

__doctests__ = ['pycreeper.utils.scheduler']

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


class RequestTest(unittest.TestCase):

    def test_basic(self):
        request_filter = RequestFilter()
        request_filter.request_seen(REQUEST[0])
        self.assertEqual(request_filter.request_seen(REQUEST[0]), True)
        self.assertEqual(request_filter.request_seen(REQUEST[1]), False)
        self.assertEqual(request_filter.request_seen(REQUEST[1]), True)
        self.assertRaises(AttributeError, request_filter.request_seen, None)

class SchedulerTest(unittest.TestCase):

    def test_basic(self):
        self.assertRaises(AttributeError, Scheduler, None)

    def test_enqueue(self):
        logger = get_logger(Settings())
        scheduler = Scheduler(logger)
        self.assertRaises(AttributeError, scheduler.enqueue_request, None)
        self.assertEqual(len(scheduler.queue), 0)
        scheduler.enqueue_request(REQUEST[0])
        self.assertEqual(len(scheduler.queue), 1)
        scheduler.enqueue_request(REQUEST[0])
        self.assertEqual(len(scheduler.queue), 1)
        scheduler.enqueue_request(REQUEST[1])
        self.assertEqual(len(scheduler.queue), 2)
        scheduler.enqueue_request(REQUEST[0])
        self.assertEqual(len(scheduler.queue), 2)

    def test_enqueue(self):
        logger = get_logger(Settings())
        scheduler = Scheduler(logger)
        self.assertIs(scheduler.next_request(), None)
        scheduler.enqueue_request(REQUEST[0])
        scheduler.enqueue_request(REQUEST[1])
        scheduler.enqueue_request(REQUEST[2])
        self.assertEqual(scheduler.next_request(), REQUEST[0])
        self.assertEqual(scheduler.next_request(), REQUEST[1])
        self.assertEqual(scheduler.next_request(), REQUEST[2])
        self.assertIs(scheduler.next_request(), None)


if __name__ == "__main__":
    unittest.main()
