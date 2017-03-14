# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Downloader """
import cookielib
import requests
from pycreeper.http.response import Response
from pycreeper.downloader_middlewares import DownloaderMiddlewareManager
from selenium.common.exceptions import TimeoutException as _TimeoutException
from pycreeper.utils.exceptions import TimeoutException
from requests.exceptions import Timeout
from pycreeper.http.headers import Headers
from urlparse import urlparse


class DownloadHandler(object):
    """ DownloadHandler """

    def __init__(self, spider, driver, driver_sem, **kwargs):
        self.settings = spider.settings
        self.logger = spider.logger
        self.session_map = {}
        self.kwargs = kwargs
        self.driver = driver
        self.driver_sem = driver_sem

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
            "timeout": self.settings["TIMEOUT"],
        }
        try:
            session = requests.Session()
            if request.cookiejar:
                session.cookies = request.cookiejar
            if request.method == 'GET':
                response = session.get(url, **kwargs)
            elif request.method == 'POST':
                if request.body:
                    kwargs.update(data=request.body)
                response = session.post(url, **kwargs)
            else:
                raise ValueError('Unacceptable HTTP verb %s' % request.method)
            # TODO: 把response的cookiejar放到request里面应该是middleware做的工作
            '''
            # handle cookie in response
            if request.cookiejar:
                cookies = self._get_cookies_from_cookiejar(response.cookies)
                for cookie in cookies:
                    request.cookiejar.set_cookie(cookie)
            '''
        except Timeout as e:
            raise TimeoutException(e.message)
        return Response(response.url, request, response.status_code,
                        response.cookies, response.content)

    def _fetch_dynamic(self, request, url):
        try:
            self.driver_sem.acquire()
            cookies = request.headers.get_cookies()
            self._removed_first_dot_in_front_of_domain(cookies)
            command_list = self._get_command_list(cookies)
            # make the current page to have the same domain with cookies
            self.driver.get(url)
            # load cookies
            for command in command_list:
                self.driver.execute_script(command)

            self.driver.set_page_load_timeout(self.settings["TIMEOUT"])
            self.driver.implicitly_wait(request.wait)
            self.driver.get(url)
            for func in request.browser_actions:
                func(self.driver)
            html = self.driver.page_source
            all_cookies = self.driver.get_cookies()

            self.driver.delete_all_cookies()
            self.driver_sem.release()
            return Response(url, request, body=html)
        except _TimeoutException as e:
            raise TimeoutException(e.message)

    def _removed_first_dot_in_front_of_domain(self, cookies):
        for cookie in cookies:
            for k in cookie:
                if k == 'domain' and str(cookie[k]).startswith('.'):
                    cookie[k] = cookie[k][1:]

    def _get_command_list(self, cookies):
        js_list = []
        for cookie in cookies:
            item_list = [cookie['name'] + '=' + cookie['value']]
            for k in ('domain', 'path', 'expiry'):
                if k in cookie and not (cookie[k] is None):
                    item_list.append(str(k) + '=' + str(cookie[k]))
            js_list.append("document.cookie = '%s';\n" % ('; '.join(item_list)))
        return js_list

    def _get_cookies_from_cookiejar(self, cj):
        result = []
        for domain in cj._cookies.keys():
            for path in cj._cookies[domain].keys():
                for cookie in cj._cookies[domain][path].values():
                    result.append(cookie)
        return result

    def _make_cookie(self, name, value):
        return cookielib.Cookie(
            version=0,
            name=name,
            value=value,
            port=None,
            port_specified=False,
            domain="court.gov.cn",
            domain_specified=True,
            domain_initial_dot=False,
            path="/",
            path_specified=True,
            secure=False,
            expires=None,
            discard=False,
            comment=None,
            comment_url=None,
            rest=None
        )


class Downloader(object):
    """ Downloader """

    def __init__(self, spider, driver, driver_sem):
        self.hanlder = DownloadHandler(spider, driver, driver_sem)
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
