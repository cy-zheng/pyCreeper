request对象和response对象
============================

request对象和response对象负责在各个PyCreeper组件之间传递信息，您在使用爬虫的过程中，会经常需要对这两个对象进行操作。

Request：自定义您的请求
-----------------------------

构造参数::

    Request(url, callback=None, method='GET', headers=None,body=None, meta=None,
            encoding='utf-8', cookiejar=None,dynamic=False, browser_actions=None, wait=0)

**url**

请求的url

**callback**

请求的回调函数，如果未定义则使用Spider.parse方法处理响应。

**method**

支持GET型和POST型请求方法，其中，POST方法只有当dynamic=False时才会被支持，
如果dynamic=True将会抛出一个AttributeError。

**headers**

该参数可以传入一个字典（dict），用于静态请求的头部信息。

**body**

该参数用于静态请求的请求体。

**meta**

该参数为字典（dict）型，用于给request携带一些参数，这些参数可能在其他模块用到。

**encoding**

请求的编码方式，用于给url和body编码。

**cookiejar**

该参数用于取出request携带的cookiejar，在构造request对象时请不要向该参数传入值，传入的cookiejar不会被PyCreeper使用到。

**dynamic**

该参数用于标记request是否是动态请求。

**browser_actions**

该参数用于定义浏览器打开指定网址之后，到提取数据之前，执行的一系列操作。该参数可以传入一个函数列表。

**wait**

该参数用于定义浏览器打开指定网址之后，到执行browser_actions中定义的函数之前，等待的时间。
当网页存在大量异步加载请求的时候，这个参数格外有用。