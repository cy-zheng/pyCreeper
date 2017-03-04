# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

""" Base Spider"""

import json

from pycreeper.conf.settings import Settings
from pycreeper.http.request import Request
from pycreeper.engine import Engine
from pycreeper.utils.log import get_logger


class Spider(object):
    """ Base Spider"""

    custom_settings = None

    def __init__(self):
        if not hasattr(self, "start_urls"):
            self.start_urls = []
        # init settings
        self.settings = Settings(self.custom_settings)
        self.logger = get_logger(self.settings)
        self.initialize()

    def initialize(self):
        """initialize
        """
        pass

    def start_requests(self):
        """start_requests
        """
        for url in self.start_urls:
            yield Request(url)

    def start(self):
        """start
        """
        engine = Engine(self)
        engine.start()

    def parse(self, response):
        """parse
        """
        raise NotImplementedError

    def process_item(self, item):
        """process item
        """
        self.logger.debug(json.dumps(item))
