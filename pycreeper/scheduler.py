# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Scheduler """

from gevent.queue import Queue
from pybloom import ScalableBloomFilter
import gevent
from pycreeper.utils.hash import request_fingerprint


class Scheduler(object):
    """ Scheduler """

    def __init__(self, spider):
        self.request_filter = RequestFilter()
        self.queue = Queue()
        self.settings = spider.settings
        self.timeout = self.settings.get('TIMEOUT', 5)
        self.download_delay = self.settings.get('DOWNLOAD_DELAY', 0)
        self.logger = spider.logger

    def enqueue_request(self, request):
        """put request
        """
        if self.request_filter.request_seen(request):
            self.logger.debug("ignore %s", request.url)
            return
        self.queue.put(request)

    def next_request(self):
        """next request
        """
        gevent.sleep(self.download_delay)
        return self.queue.get(timeout=self.timeout * 3)

    def __len__(self):
        return self.queue.qsize()


class RequestFilter(object):
    """ RequestFilter """

    def __init__(self):
        self.sbf = ScalableBloomFilter(
            mode=ScalableBloomFilter.SMALL_SET_GROWTH)

    def request_seen(self, request):
        """request seen
        """
        finger = request_fingerprint(request)
        if finger in self.sbf:
            return True
        self.sbf.add(finger)
        return False
