# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import json
import HTMLParser
from pycreeper.spider import Spider
from pycreeper.http.request import Request
from selenium.webdriver.common.keys import Keys
import gevent
from lxml import etree
from selenium.common.exceptions import NoSuchElementException

parser = HTMLParser.HTMLParser()

class Jd_Spider(Spider):

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'pycreeper.downloader_middlewares.middlewares.UserAgentMiddleware': 100,
            'pycreeper.downloader_middlewares.middlewares.RetryMiddleware': 200,
            'pycreeper.downloader_middlewares.cookies_middlewares.CookiesMiddleware': 300,
            'pycreeper.downloader_middlewares.middlewares.EncodingDiscriminateMiddleware': 400
        },
        'DRIVER': 'Chrome',
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT_LIST': [
            '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36''',
        ]
    }

    def start_requests(self):
        def _search(driver):
            driver.find_element_by_id('key').send_keys(u"联想笔记本", Keys.ENTER)
            gevent.sleep(3)
            self._jump_guide(driver)
            gevent.sleep(3)

        yield Request(url='https://www.jd.com/',
                      meta={"cookiejar": "jd"},
                      callback=self.parse_list,
                      dynamic=True,
                      browser_actions=[_search]
                      )

    def _jump_guide(self, driver):
        try:
            driver.find_element_by_xpath('//*[@id="guide-price"]/div[2]/a').click()
        except NoSuchElementException as e:
            pass

    def parse_list(self, response):
        html = response.body
        selector = etree.HTML(html)
        links = selector.xpath('//div[@class="p-img"]/a')
        titles = selector.xpath('//div[@class="p-name p-name-type-2"]/a/em')
        imgs = selector.xpath('//div[@class="p-img"]/a/img')
        prices = selector.xpath('//div[@class="p-price"]/strong/i')
        for i in range(len(links)):
            try:
                yield {
                    'path': links[i].attrib["href"] if 'http' in links[i].attrib["href"]
                                        else 'http:' + links[i].attrib["href"],
                    'title': parser.unescape(etree.tostring(titles[i], pretty_print=True)),
                    'img': imgs[i].attrib["src"] if 'http' in imgs[i].attrib["src"]
                          else 'http:' + imgs[i].attrib["src"],
                    'price': prices[i].text,
                }
            except Exception as e:
                pass

            url = response.url

        def _next_page(driver):
            self._jump_guide(driver)
            driver.find_element_by_xpath('//*[@id="J_bottomPage"]/span[1]/a[9]').click()
            self._jump_guide(driver)

        yield Request(url=url,
                      meta={"cookiejar": "jd"},
                      callback=self.parse_list,
                      dynamic=True,
                      browser_actions=[_next_page]
                      )

    def process_item(self, item):
        print json.dumps(item, ensure_ascii=False).encode('GBK', 'ignore')

if __name__ == "__main__":
    spider = Jd_Spider()
    spider.start()
