# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import random
import time
from urlparse import urlparse
from logging import Logger
import chardet
import gevent
from pycreeper.downloader_middlewares import DownloaderMiddleware
from pycreeper.utils.exceptions import TimeoutException
from collections import deque


class RetryMiddleware(DownloaderMiddleware):
    """ Retry Middleware """

    RETRY_EXCEPTIONS = TimeoutException

    def __init__(self, settings, logger):
        self.max_retry_count = settings.get_int("RETRY_COUNT")
        self.retry_status_codes = settings.get_list("RETRY_STATUS_CODES")
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_response(self, request, response):
        """process response
        """
        if request.meta.get("dont_retry", False):
            return response
        if response.status in self.retry_status_codes:
            return self._retry(request) or response
        return response

    def process_exception(self, request, exception):
        """process exception
        """
        if isinstance(exception, self.RETRY_EXCEPTIONS) \
                and request.meta.get("dont_retry", False):
            return self._retry(request)

    def _retry(self, request):
        """retry
        """
        retry_count = request.meta.get("retry_count", 0) + 1
        if retry_count <= self.max_retry_count:
            retry_request = request.copy()
            retry_request.meta["retry_count"] = retry_count
            return retry_request


class UserAgentMiddleware(DownloaderMiddleware):
    """ UserAgent Middleware """

    def __init__(self, settings, logger):
        self.user_agent_list = settings.get_list("USER_AGENT_LIST")
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_request(self, request):
        """process request

        static requests only.
        """
        if not request.dynamic:
            request.headers["User-Agent"] = random.choice(self.user_agent_list)


class ProxyMiddleware(DownloaderMiddleware):
    """ Proxy Middleware """

    def __init__(self, settings, logger):
        self.host_time_queue = deque()
        self.proxy_interval = settings["PROXY_INTERVAL"]
        self.proxy_list = settings["PROXY_LIST"]
        for proxy in self.proxy_list:
            self.host_time_queue.append((proxy, 0))
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_request(self, request):
        """process request

        static requests only.
        """
        if not request.dynamic:
            request.meta["proxy"] = {
                "http": self._get_proxy(),
            }

    def _get_proxy(self):
        """get proxy
        """
        proxy, latest = self.host_time_queue.popleft()
        interval = time.time() - latest
        if interval < self.proxy_interval:
            self.logger.info("Proxy %s waitting ...", proxy)
            gevent.sleep(self.proxy_interval - interval)
        self.host_time_queue.append((proxy, time.time()))
        return "http://%s" % proxy


class EncodingDiscriminateMiddleware(DownloaderMiddleware):
    """ Encoding Discriminate Middleware """

    ENCODING_MAP = {}

    def __init__(self, settings, logger):
        self.settings = settings
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_response(self, request, response):
        """process respoonse
        :param request:
        :param response:
        """
        netloc = urlparse(request.url).netloc
        content = response.body
        if self.ENCODING_MAP.get(netloc) is None:
            encoding = chardet.detect(content)["encoding"]
            encoding = "GB18030" \
                if encoding.upper() in ("GBK", "GB2312") else encoding
            self.ENCODING_MAP[netloc] = encoding
        body = content.decode(self.ENCODING_MAP[netloc], "replace")
        return response.copy(body=body)
