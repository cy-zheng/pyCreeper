# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Downloader """

import requests
from importlib import import_module
from pycreeper.http.response import Response
from pycreeper.downloader_middlewares import DownloaderMiddlewareManager
from gevent.lock import BoundedSemaphore

DRIVER_MODULE = 'selenium.webdriver'


class DownloadHandler(object):
    """ DownloadHandler """

    def __init__(self, spider, **kwargs):
        self.settings = spider.settings
        self.logger = spider.logger
        self.session_map = {}
        self.kwargs = kwargs
        self.dynamic = self.settings.get('DYNAMIC_CRAWL', False)
        if self.dynamic:
            module_path = DRIVER_MODULE
            module = import_module(module_path)
            self.driver = getattr(module,
                                  self.settings.get('DRIVER'))()
        else:
            self.driver = None
        self.driver_sem = BoundedSemaphore(1)

    def fetch(self, request):
        """fetch
        """
        # TODO: 应该把proxy拿出去做成一个中间件
        '''
        proxy = request.meta.get("proxy")
        if proxy:
            kwargs["proxies"] = {"http:": proxy}
            self.logger.info("Use proxy %s", proxy)
        kwargs.update(self.kwargs)
        '''
        url = request.url
        self.logger.info("processing %s", url)
        if request.dynamic:
            return self._fetch_dynamic(request, url)
        else:
            return self._fetch_static(request, url)

    def _fetch_static(self, request, url):
        kwargs = {
            "headers": request.headers.to_dict(),
            "timeout": self.settings["TIMEOUT"],
        }
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

    def _fetch_dynamic(self, request, url):
        self.driver_sem.acquire()
        # TODO:实现Header获取cookie字典
        cookies = request.headers.get_cookies()
        self.driver.add_cookie(cookies)
        self.driver.set_page_load_timeout(self.settings["TIMEOUT"])
        self.driver.implicitly_wait(request.wait)
        self.driver.get(url)
        for func in request.browser_actions:
            func(self.driver)
        html = self.driver.page_source
        self.driver.delete_all_cookies()
        self.driver_sem.release()
        return Response(url, request, body=html)



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
