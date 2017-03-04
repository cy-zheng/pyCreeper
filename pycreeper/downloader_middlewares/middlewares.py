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


class RetryMiddleware(DownloaderMiddleware):
    """ Retry Middleware """

    RETRY_EXCEPTIONS = ()

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
        """
        request.headers["User-Agent"] = random.choice(self.user_agent_list)


class ProxyMiddleware(DownloaderMiddleware):
    """ Proxy Middleware """

    def __init__(self, settings, logger):
        self.host_time_map = {}
        self.proxy_interval = settings["PROXY_INTERVAL"]
        self.proxy_list = settings["PROXY_LIST"]
        self.proxy_enable = settings["PROXY_ENABLED"]
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_request(self, request):
        """process request
        """
        if self.proxy_enable:
            request.meta["proxy"] = self._get_proxy()

    def _get_proxy(self):
        """get proxy
        """
        # TODO: 这段代码很容易长时间gevent.sleep。能否切换代理？
        proxy = random.choice(self.proxy_list).strip()
        host, _ = proxy.split(":")
        latest = self.host_time_map.get(host, 0)
        interval = time.time() - latest
        if interval < self.proxy_interval:
            self.logger.info("Proxy %s waitting ...", proxy)
            gevent.sleep(self.proxy_interval)
        self.host_time_map[host] = time.time()
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
