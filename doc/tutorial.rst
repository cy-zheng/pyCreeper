PyCreeper初探
==============
PyCreeper是一个用来快速提取网页内容的信息采集（爬虫）框架。项目底层异步网络I/O使用 **Gevent** 协程库，将网络请求分为静态请求和动态请求，
静态请求交给 **Requests** 处理，动态请求则使用 **Selenium.Webdriver** 加载。

在设计这个项目的过程中，我参考了很多 **Scrapy** （项目网站: https://scrapy.org/）的架构和实现方式。Scrapy是一个非常棒的爬虫框架，
我之前花了很多心血在Scrapy框架之上！

这篇PyCreeper初探会编写一个简单的爬虫例子，让您明白PyCreeper大致的工作流程，使您快速上手。

目标任务
---------
知乎（https://www.zhihu.com/）与Quora类似，是一个分享知识提出问题的平台。我们的Demo任务是模拟登陆知乎，保存Cookie，
之后发出一系列静态请求，获取首页的问题题目与描述。

由于模拟登陆一步我们采用了基于Selenium.Webdriver的动态请求处理，所以你可以抛开复杂的抓包与分析代码，只需要点几个按钮，
就像在真实环境登录知乎一样简单便利！


定义一个爬虫
-------------
定义一个爬虫类需要需要继承Spider类，代码如下::

    from pycreeper.spider import Spider

    class Zhihu_Spider(Spider):
        pass

选择中间件MiddleWares
----------------------
对于Spider的中间件选择，通过修改custom_settings对象实现::

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'pycreeper.downloader_middlewares.middlewares.UserAgentMiddleware': 100,
            'pycreeper.downloader_middlewares.middlewares.RetryMiddleware': 200,
            'pycreeper.downloader_middlewares.cookies_middlewares.CookiesMiddleware': 300
        },
        'DRIVER': 'Chrome',
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT_LIST': [
           '''Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36
            (KHTML, like Gecko) Chrome/57.0.2987.98 Safari/537.36''',
        ]
    }

其中，DOWNLOADER_MIDDLEWARES是这个爬虫爬取过程中使用的中间件。UserAgentMiddleware提供了一种简单的控制请求User-Agent的方式（只对静态请求有效，
动态请求的UA取决于使用的WebDriver）。RetryMiddleware对失败的请求（错误的返回码，超时等）进行多次重试。CookiesMiddleware在全体的请求之间共享CookieJar池，
一组请求可以共享一个CookieJar，CookiesMiddleware维护CookieJar的有效性与一致性。

DRIVER表明了动态请求的浏览器，这里我们使用Chrome。

DOWNLOAD_DELAY表明了下载之间的延迟时间（秒），这个选项当网站有某种防爬策略时还是很有用的。

USER_AGENT_LIST中包含请求使用的User-Agent，UserAgentMiddleware会从中随机取出一个来使用。


最开始的请求
-------------
下面这段代码通过重写start_requests方法yield一个PyCreeper请求::

    def start_requests(self):

        def _login(driver):
            driver.find_element_by_name('account').send_keys("username")
            driver.find_element_by_name('password').send_keys("password")
            driver.find_element_by_xpath('/html/body/div[1]/div/div[2]/div[2]/form/div[2]/button').click()
            gevent.sleep(5)

        yield Request(url='https://www.zhihu.com/#signin', meta={"cookiejar": "zhihu"},
                      callback=self.after_login, dynamic=True, browser_actions=[_login])
                      
在Request对象的参数中，dynamic=True表明这是一个动态请求，将会调用WebDriver加载，
而browser_actions=[_login]则定义了浏览器加载完成之后进行的动作。本例中输入了用户名与密码，然后点击登录。
gevent.sleep(5)则是令爬虫等待浏览器加载完成。

meta={"cookiejar": "zhihu"}这个选项表明本次请求产生的Cookie将会被存储在名为zhihu的CookieJar当中

callback=self.after_login定义了本次响应的处理函数。

接下来？
--------
接下来一步将在知乎首页中提取问题链接，发出静态问题请求::

    def after_login(self, response):
        html = response.body
        selector = etree.HTML(html)
        links = selector.xpath('//a[@class="question_link"]')
        for link in links:
            yield Request('https://www.zhihu.com' + link.attrib["href"],
                          meta={"cookiejar": "zhihu"}, callback=self.get_item)

response.body存储了响应的内容。我们使用了lxml提取html文本中的标签，然后发出一系列静态请求。

在获得问题页面的数据之后，我们需要做的是提取出其中的问题标题与详情::

    def get_item(self, response):
        html = response.body
        selector = etree.HTML(html)
        head = selector.xpath('//h1[@class="QuestionHeader-title"]')[0].text
        body = selector.xpath('//span[@class="RichText"]')[0].text
        yield {
            'head': head,
            'body': body
        }
        
过程与上个函数类似，通过xpath定位元素。

处理你获得的数据
-----------------
处理数据通过重写process_item方法实现::

    def process_item(self, item):
        print json.dumps(item, ensure_ascii=False)
       
这里我们只是将结果打印。

运行你的爬虫
-------------
最后我们通过这样一段代码运行爬虫::

    if __name__ == "__main__":
        spider = Zhihu_Spider()
        spider.start()
        
完整的代码如下::

    # -*- coding:utf-8 -*-

    from pycreeper.spider import Spider
    from pycreeper.http.request import Request
    from lxml import etree
    import json
    import gevent


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
                driver.find_element_by_name('account').send_keys("username")
                driver.find_element_by_name('password').send_keys("password")
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
            print json.dumps(item, ensure_ascii=False)

    if __name__ == "__main__":
        spider = Zhihu_Spider()
        spider.start()


写在后面
---------
项目已经通过PyPi发布，您可以通过以下命令下载::

    pip install pycreeper

未来我们将会引入Docker的支持。

目前项目刚刚发布1.0.0版本，如果在使用时，遇到各种问题，我们都欢迎您反馈给我们，您可以通过github，
项目主页：https://github.com/ZcyAndWt/pyCreeper，也可以通过邮件，作者的邮箱：zhengchenyu.backend@gmail.com。

如果您使用中，觉得本项目有可取之处，提高了您爬取数据的效率，希望您能在github上star本项目。
您的支持是我们前进最大的动力！





