# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Downloader """

import urlparse

import requests

from pycreeper.http.response import Response
from pycreeper.downloader_middlewares import DownloaderMiddlewareManager


class DownloadHandler(object):
    """ DownloadHandler """

    def __init__(self, spider, keep_alive=True, **kwargs):
        self.keep_alive = keep_alive
        self.settings = spider.settings
        self.logger = spider.logger
        self.session_map = {}
        self.kwargs = kwargs

    def _get_session(self, url):
        """get session

        @url, str, url
        """
        netloc = urlparse.urlparse(url).netloc
        if self.keep_alive:
            if netloc not in self.session_map:
                self.session_map[netloc] = requests.Session()
            return self.session_map[netloc]
        return requests.Session()

    def fetch(self, request):
        """fetch
        """
        proxy = request.meta.get("proxy")
        kwargs = {
            "headers": request.headers.to_dict(),
            "timeout": self.settings["TIMEOUT"],
        }
        if proxy:
            kwargs["proxies"] = {"http:": proxy}
            self.logger.info("Use proxy %s", proxy)
        kwargs.update(self.kwargs)
        url = request.url
        session = self._get_session(url)
        self.logger.info("processing %s", url)
        if request.method == 'GET':
            response = requests.get(url, allow_redirects=False, **kwargs)
        elif request.method == 'POST':
            if request.body:
                kwargs.update(data=request.body)
            response = requests.post(url, **kwargs)
        else:
            raise ValueError('Unacceptable HTTP verb %s' % request.method)
        return Response(response.url, request, response.status_code,
                        response.headers, response.content)


class Downloader(object):
    """ Downloader """

    def __init__(self, spider):
        self.hanlder = DownloadHandler(spider)
        self.middleware = DownloaderMiddlewareManager(spider)

    def fetch(self, request, spider):
        """fetch

        @request, Request, 请求
        """
        return self.middleware.download(self._download, request)

    def _download(self, request):
        """download
        """
        return self.hanlder.fetch(request)
