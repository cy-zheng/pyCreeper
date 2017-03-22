settings：项目设置
=====================

这篇文档主要介绍项目的设定（settings）参数和其默认值。

如何覆盖项目的默认设定？
--------------------------

可以在您定义的爬虫中设置 **custom_settings** 属性，覆盖掉PyCreeper的默认设定。

示例::

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

设定的可选参数和默认值
---------------------------

**LOG_LEVEL** 

该参数为byte类型，默认值为DEBUG，该参数控制PyCreeper日志的输出等级。

**RETRY_COUNT** 

该参数为数值型，默认值为3，表示对于失败请求的最大尝试次数（该参数只对静态请求有效）。

**RETRY_STATUS_CODES** 

该参数为list型，默认值为[500, 502, 503, 504, 400, 403, 408]，表示返回码在列表中的请求将会被重发（该参数只对静态请求有效）。

**TIMEOUT** 

该参数为数值型，默认值为5，表示发出请求定义的超时时间（秒）。

**MAX_REQUEST_SIZE** 

该参数为int型，默认值为20，表示可以同时进行的静态请求个数（该参数只对静态请求有效）。

**USER_AGENT_LIST** 

该参数为list型，默认值为空列表，表示发送请求时可以携带的User-Agent（需要使用UserAgentMiddleware，该参数只对静态请求有效）。

**DOWNLOADER_MIDDLEWARES** 

该参数为dict型，默认值为空字典，表示使用的下载器中间件。字典的key值为希望使用的中间件的reference，
value值为该中间件的优先级，优先级越高的中间件将会越先被使用。

**DYNAMIC_CRAWL** 

该参数为bool型，默认值为True，表示引擎是否加载WebDriver。如果在设为False的情况下发出了一系列动态请求，将会引发一系列异常。

**DRIVER** 

该参数为byte型，默认值为Firefox，表示PyCreeper使用的Driver类型。可以选择任意一种Selenium支持的Driver，前提是需要配置好Driver的相关环境。

**DRIVER_INIT_KWARGS** 

该参数为dict型，默认为空字典，表示启动Driver时传入的参数，您可以通过定义该值修改Driver的属性。

**DOWNLOAD_DELAY** 

该参数为数值型，默认值为0，表示下载延迟（秒）。

**PROXY_INTERVAL** 

该参数为数值型，默认值为3，表示每个代理使用的最大时间。使用proxy需要搭配ProxyMiddleware，
并且此处的proxy只对静态请求有效。如果您想配置动态请求的proxy，可以设置DRIVER_INIT_KWARGS参数，在Driver启动时传入配置信息。

**PROXY_LIST** 

该参数为list型，默认为空数组，表示请求可以用到的proxy。格式为'IP:端口号'。

**STATIC_REQUEST_SSL_VERIFY** 

该参数为bool型，默认值为True，表示发起静态请求是，是否进行ssl认证。
该参数用于在使用代理的情况下，https认证失败的情况。