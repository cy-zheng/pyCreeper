# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import json

from pycreeper.spider import Spider
from pycreeper.http.request import Request


class CrawlerTest(Spider):
    start_urls = [
        'http://haojiazhang123.com/lianzi/get_lianzi_book_list.json?grade=1',
    ]

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'pycreeper.downloader_middlewares.middlewares.UserAgentMiddleware': 100,
            'pycreeper.downloader_middlewares.middlewares.RetryMiddleware': 200,
        }
    }

    def parse(self, response):
        grade = int(response.request.url.split('grade=')[-1])
        yield json.loads(response.body)
        if grade < 6:
            yield Request('http://haojiazhang123.com/lianzi/get_lianzi_book_list.json?grade=%d' % (grade + 1))


if __name__ == "__main__":
    spider = CrawlerTest()
    spider.start()
