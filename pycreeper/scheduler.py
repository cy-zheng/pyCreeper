# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Scheduler """

from gevent.queue import Queue
from logging import Logger
from pybloom import ScalableBloomFilter
from utils.hash import request_fingerprint


class Scheduler(object):
    """ Scheduler """

    def __init__(self, logger):
        self.request_filter = RequestFilter()
        self.queue = Queue()
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def enqueue_request(self, request):
        """put request
        """
        if not request.dont_filter \
                and self.request_filter.request_seen(request):
            self.logger.warn("ignore %s", request.url)
            return
        self.queue.put(request)

    def next_request(self):
        """next request
        """
        if self.queue.empty():
            return None
        return self.queue.get()

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
