#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

from pycreeper.downloader_middlewares import DownloaderMiddleware
import six
from collections import defaultdict

from pycreeper.http.response import Response
from pycreeper.http.cookies import CookieJar


class CookiesMiddleware(DownloaderMiddleware):
    """This middleware enables working with sites that need cookies"""

    def __init__(self, settings, logger):
        self.jars = defaultdict(CookieJar)
        self.settings = settings
        self.logger = logger

    def process_request(self, request):
        if request.meta.get('dont_merge_cookies', False):
            return
        if not request.meta or request.meta.get("cookiejar", None) is None:
            return
        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        # set Cookie header
        request.headers.pop('Cookie', None)
        jar.add_cookie_header(request)

    def process_response(self, request, response):
        if request.meta.get('dont_merge_cookies', False):
            return response
        if not request.meta or request.meta.get("cookiejar", None) is None:
            return response
        # extract cookies from Set-Cookie and drop invalid/expired cookies
        cookiejarkey = request.meta.get("cookiejar")
        jar = self.jars[cookiejarkey]
        jar.extract_cookies(response, request)

        return response

    def _format_cookie(self, cookie):
        # build cookie string
        cookie_str = '%s=%s' % (cookie['name'], cookie['value'])

        if cookie.get('path', None):
            cookie_str += '; Path=%s' % cookie['path']
        if cookie.get('domain', None):
            cookie_str += '; Domain=%s' % cookie['domain']

        return cookie_str