# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Engine """

from gevent import monkey
monkey.patch_all()

import logging

import gevent
from gevent.pool import Pool

from scheduler import Scheduler
from downloader.downloader import Downloader
from utils.gevent import spawn, join_all
from utils import result2list
from http.request import Request


class Engine(object):
    """ Engine """

    def __init__(self, spider):
        # TODO: logger is related to settings, so we should maintain a global logger.
        self.spider = spider
        self.scheduler = Scheduler()
        self.downloader = Downloader(spider)
        self.settings = spider.settings
        max_request_size = self.settings["MAX_REQUEST_SIZE"]
        self.pool = Pool(size=max_request_size)

    def start(self):
        """start
        """
        start_requests = iter(self.spider.start_requests())
        self.execute(self.spider, start_requests)

    def execute(self, spider, start_requests):
        """execute
        """
        self.start_requests = start_requests
        all_routines = []
        all_routines.append(spawn(self._init_start_requests))
        all_routines.append(spawn(self._next_request, spider))
        join_all(all_routines)

    def _init_start_requests(self):
        """init start requests
        """
        for req in self.start_requests:
            self.crawl(req)

    def _next_request(self, spider):
        """next request
        """
        while True:
            request = self.scheduler.next_request()
            if not request:
                gevent.sleep(0)
                continue
            self.pool.spawn(
                self._process_request, request, spider)

    def _process_request(self, request, spider):
        """process request
        """
        try:
            response = self.download(request, spider)
        except Exception as exc:
            logging.error("download error: %s", str(exc), exc_info=True)
        else:
            self._handle_downloader_output(response, request, spider)
            return response

    def download(self, request, spider):
        """ download

        Download a request, use self.downloader.fetch

        """
        response = self.downloader.fetch(request, spider)
        response.request = request
        return response

    def _handle_downloader_output(self, response, request, spider):
        """hanlde downloader output

        TODO: why downloader could return a Request?

        """
        if isinstance(response, Request):
            self.crawl(response)
            return

        self.process_response(response, request, spider)

    def process_response(self, response, request, spider):
        """process response

        Use request.callback or spider.parse to process response

        """
        callback = request.callback or spider.parse
        result = callback(response)
        ret = result2list(result)
        self.handle_spider_output(ret, spider)

    def handle_spider_output(self, result, spider):
        """handle spider output

        If a spider return a request, crawling it.
        Else if it's a dict, use self.process_item.

        """
        for item in result:
            if item is None:
                continue
            elif isinstance(item, Request):
                self.crawl(item)
            elif isinstance(item, dict):
                self.process_item(item, spider)
            else:
                logging.error("Spider must return Request, dict or None")

    def process_item(self, item, spider):
        """handle item

        Use spider.process_item function.

        """
        spider.process_item(item)

    def crawl(self, request):
        """crawl request

        Add request to scheduler's queue.

        """
        self.scheduler.enqueue_request(request)
