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
import six
from pycreeper.utils import _get_cookies_from_cookiejar
import gevent


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
        url = request.url
        if request.dynamic:
            return self._fetch_dynamic(request, url)
        else:
            return self._fetch_static(request, url)

    def _fetch_static(self, request, url):
        self.logger.info("processing static page %s", url)
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
        except Timeout as e:
            raise TimeoutException(e.message)
        return Response(response.url, request, response.status_code,
                        response.cookies, response.content)

    def _fetch_dynamic(self, request, url):
        self.logger.info("processing dynamic page %s", url)
        try:
            self.driver_sem.acquire()
            if request.cookiejar:
                cookies = _get_cookies_from_cookiejar(request.cookiejar)
                cookies = self._covert_cookies_to_dict(cookies)
                #self._removed_first_dot_in_front_of_domain(cookies)
                command_list = self._get_command_list(cookies)
                # make the current page to have the same domain with cookies
                self.driver.get(url)
                # load cookies
                for command in command_list:
                    self.driver.execute_script(command)

            self.driver.set_page_load_timeout(self.settings["TIMEOUT"])
            self.driver.get(url)
            gevent.sleep(request.wait)
            for func in request.browser_actions:
                func(self.driver)
            html = self.driver.page_source

            # generate cookies
            all_cookies = self.driver.get_cookies()
            self.driver.delete_all_cookies()
            self.driver_sem.release()

            all_cookies = self._to_byte(all_cookies)
            cookies = [self._make_cookie(**d) for d in all_cookies]

            # set cookies to cookiejar
            cj = cookielib.CookieJar()
            for cookie in cookies:
                cj.set_cookie(cookie)
            return Response(url, request, cookiejar=cj, body=html)
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

    def _make_cookie(self, **kwargs):
        return cookielib.Cookie(
            version=0,
            name=kwargs.get('name', None),
            value=kwargs.get('value', None),
            port=None,
            port_specified=False,
            domain=kwargs.get('domain', None),
            domain_specified=True,
            domain_initial_dot=False,
            path=kwargs.get('path', None),
            path_specified=True,
            secure=False,
            expires=kwargs.get('expires', None),
            discard=False,
            comment=None,
            comment_url=None,
            rest=None
        )

    def _covert_cookies_to_dict(self, cookies):
        result = []
        for cookie in cookies:
            cookie_dict = {}
            for key in ['name', 'value', 'domain', 'path', 'expires']:
                if getattr(cookie, key):
                    cookie_dict[key] = getattr(cookie, key)
            result.append(cookie_dict)
        return result

    def _to_byte(self, cookies):
        result = []
        for cookie in cookies:
            temp = {}
            for key in cookie.keys():
                temp[key.encode('utf-8') if isinstance(key, six.text_type) else key] = \
                    cookie[key].encode('utf-8') if isinstance(cookie[key], six.text_type) else cookie[key]
            result.append(temp)
        return result




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
