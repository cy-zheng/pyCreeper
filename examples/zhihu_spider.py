# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import json

from pycreeper.spider import Spider
from pycreeper.http.request import Request
import gevent
from lxml import etree

class Zhihu_Spider(Spider):

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'pycreeper.downloader_middlewares.middlewares.UserAgentMiddleware': 100,
            'pycreeper.downloader_middlewares.middlewares.RetryMiddleware': 200,
            'pycreeper.downloader_middlewares.cookies_middlewares.CookiesMiddleware': 300
        },
        'DRIVER': 'Chrome',
        'DOWNLOAD_DELAY': 2,
        'STATIC_REQUEST_SSL_VERIFY': False,
        'USER_AGENT_LIST': [
            '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36''',
        ]
    }

    def start_requests(self):

        def _login(driver):
            driver.find_element_by_name('account').send_keys("15501277123")
            driver.find_element_by_name('password').send_keys("zcymichael")
            driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[2]/button').click()
            gevent.sleep(5)

        yield Request(url='https://www.zhihu.com/#signin', meta={"cookiejar": "zhihu"},
                      callback=self.after_login, dynamic=True, browser_actions=[_login])

    def after_login(self, response):
        html = response.body
        selector = etree.HTML(html)
        links = selector.xpath('//a[@class="question_link"]')
        for link in links:
            yield Request('https://www.zhihu.com' + link.attrib["href"],
                          meta={"cookiejar": "zhihu"}, callback=self.get_item)

    def get_item(self, response):
        html = response.body
        selector = etree.HTML(html)
        head = selector.xpath('//h1[@class="QuestionHeader-title"]')[0].text
        body = selector.xpath('//span[@class="RichText"]')[0].text
        yield {
            'head': head,
            'body': body
        }

    def process_item(self, item):
        print json.dumps(item, ensure_ascii=False).encode('GBK', 'ignore')

if __name__ == "__main__":
    spider = Zhihu_Spider()
    spider.start()
