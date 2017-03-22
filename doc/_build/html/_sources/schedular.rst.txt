schedular：调度器
============================

调度器实现的核心是gevent之中的Queue和布隆过滤器
（Wiki: https://en.wikipedia.org/wiki/Bloom_filter）。
其中，Queue保证了多个Downloader协程读取队列时的协程安全，布隆过滤器则提供了url去重功能。

将请求入队：enqueue_request(request)
--------------------------------------------------

request入队时，首先使用布隆过滤器检查url是否已经抓取过。如果没有抓取过则直接入队，
如果抓取过，则会输出一条logging.DEBUG信息，表示忽略了这个url。

取得队列中的请求：next_request()
-----------------------------------------------

这个方法将会从Queue中取出一条request。如果在 **custom_settings** 中设置了 **DOWNLOAD_DELAY**
项目的话，每次取出request会等待一个固定的时间。

PyCreeper将 **TIMEOUT** 值的3倍作为检验爬虫结束的标志。具体是指，如果3*TIMEOUT时间之内Queue为空的话，
那么则认为爬取任务全部结束，爬虫退出。

