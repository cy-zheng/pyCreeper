#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

"""Dowloader Midlleware"""

from collections import defaultdict

from importlib import import_module

from pycreeper.utils import call_func, sorted_priority_dict
from pycreeper.http.request import Request


class DownloaderMiddleware(object):
    """ DownloaderMiddleware iterface """

    pass


class DownloaderMiddlewareManager(object):
    """ DownloaderMiddlewareManager """

    def __init__(self, spider):
        self.settings = spider.settings
        self.logger = spider.logger
        self.methods = defaultdict(list)
        self.middlewares = self.load_middleware()
        for miw in self.middlewares:
            self._add_middleware(miw)

    def load_middleware(self):
        """load middleware
        """
        middlewares = []
        modules = sorted_priority_dict(
            self.settings.get('DOWNLOADER_MIDDLEWARES', {})
        )
        for module_name in modules:
            module = import_module('.'.join(module_name.split('.')[:-1]))
            middleware_class = getattr(module, module_name.split('.')[-1])
            middlewares.append(middleware_class(self.settings, self.logger))
        return middlewares

    def _add_middleware(self, miw):
        """add middleware
        """
        if hasattr(miw, "process_request"):
            self.methods["process_request"].append(miw.process_request)
        if hasattr(miw, "process_response"):
            self.methods["process_response"].insert(0, miw.process_response)
        if hasattr(miw, "process_exception"):
            self.methods["process_exception"].insert(0, miw.process_exception)

    def download(self, download_func, request):
        """download
        """

        def process_request(request):
            """ process request """
            for method in self.methods["process_request"]:
                method(request)
            return download_func(request)

        def process_response(response):
            """ process response """
            for method in self.methods["process_response"]:
                response = method(request, response)
                if isinstance(response, Request):
                    return response
            return response

        def process_exception(exception):
            """ process exception """
            for method in self.methods["process_exception"]:
                response = method(request, exception)
                if response:
                    return response
            return exception

        return call_func(process_request, process_exception,
                         process_response, request)
