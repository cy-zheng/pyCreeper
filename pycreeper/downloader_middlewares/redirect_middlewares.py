#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'


from pycreeper.downloader_middlewares import DownloaderMiddleware
import six
from collections import defaultdict
from logging import Logger
from urlparse import urlparse, urlunparse
from pycreeper.http.response import Response
from pycreeper.http.cookies import CookieJar

REDIRECT_STATUS = [301, 302]


class RedirectMiddleware(DownloaderMiddleware):

    def __init__(self, settings, logger):
        self.max_redirect_count = settings.get_int("MAX_REDIRECT_COUNT")
        if not isinstance(logger, Logger):
            raise AttributeError('logger must be instance of logging.Logger')
        self.logger = logger

    def process_response(self, request, response):
        """process response
        """
        if request.meta.get("dont_redirect", False):
            return response
        if int(response.status) in REDIRECT_STATUS:
            return self._redirect(response) or response
        return response

    def _redirect(self, response):
        """retry
        """
        redirect_count = response.request.meta.get("redirect_count", 0) + 1
        if redirect_count <= self.max_redirect_count:
            locate = urlparse(response.headers.get('location'))
            former = urlparse(response.request.url)
            url = self._handle_url(former, locate)
            redirect_request = response.request.copy()
            redirect_request.url = url
            redirect_request.meta["redirect_count"] = redirect_count
            return redirect_request

    def _handle_url(self, former, locate):
        if not locate.scheme and not locate.netloc:
            former = list(former)
            former[2] = locate.path
            return urlunparse(former)
        else:
            former = list(former)
            former[0] = locate.scheme
            former[1] = locate.netloc
            former[2] = locate.path
            return urlunparse(former)
