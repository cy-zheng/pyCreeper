#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

from pycreeper.downloader_middlewares import DownloaderMiddleware
import six
from collections import defaultdict
from pycreeper.utils import _get_cookies_from_cookiejar
from pycreeper.http.response import Response
from cookielib import CookieJar


class CookiesMiddleware(DownloaderMiddleware):
    """This middleware enables working with sites that need cookies"""

    def __init__(self, settings, logger):
        self.jars = defaultdict(CookieJar)
        self.settings = settings
        self.logger = logger

    def process_request(self, request):
        if not request.meta or request.meta.get("cookiejar", None) is None:
            return
        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        # set CookieJar
        request.cookiejar = jar

    def process_response(self, request, response):
        if not request.meta or request.meta.get("cookiejar", None) is None:
            return response
        # extract cookies from response.cookiejar
        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        cookies = _get_cookies_from_cookiejar(response.cookiejar)
        for cookie in cookies:
            jar.set_cookie(cookie)
        return response