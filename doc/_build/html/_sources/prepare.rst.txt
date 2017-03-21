使用前的准备
==============
我们假定您已经安装了Python2.7及以上版本，若没有安装，请参考Python官网（https://www.python.org/）选择合适的版本进行安装。

PyCreeper对于以下几个库存在依赖关系：

 * gevent
 * importlib
 * requests 
 * chardet
 * w3lib 
 * six
 * pybloom
 * Selenium
 
当然，如果您选择使用pip安装本项目，那么依赖库会自动安装到您的电脑内（至少理论上会是这样）。

使用pip安装项目::

    pip install pycreeper

配置Selenium Driver
---------------------
当您希望调用指定的浏览器时，Selenium需要您安装指定浏览器的接口。
举例来说，如果您希望使用Chrome加载请求，您需要下载安装 *Chromedriver* （https://sites.google.com/a/chromium.org/chromedriver/downloads），
然后将该程序放在您的PATH之下，确保Python能访问到它。

几个常用的Driver：

============== =======================================================================
名称           link
============== =======================================================================
Chrome         https://sites.google.com/a/chromium.org/chromedriver/downloads
Firefox        https://github.com/mozilla/geckodriver/releases
PhantomJS      http://phantomjs.org/download.html
============== =======================================================================

其中，PhantomJS是一款无界面化WebKit，当您在无GUI设备的情况下，该浏览器是您最好的选择。

对于Selenium更详细的配置，请参考 http://selenium-python.readthedocs.io/
