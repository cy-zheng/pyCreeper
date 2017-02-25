# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'


import unittest
import logging

from pycreeper.conf.settings import Settings
from pycreeper.utils.log import get_logger


class SettingsTest(unittest.TestCase):

    def test_get_logger(self):
        settings = Settings()
        logger = get_logger(settings, 'testLogger')
        self.assertEqual(logger.level, logging.DEBUG)

        settings.set('LOG_LEVEL', 'INFO')
        logger = get_logger(settings, 'testLogger')
        self.assertEqual(logger.level, logging.INFO)

        settings.set('LOG_LEVEL', 'foo')
        self.assertRaises(ValueError, get_logger, settings, 'testLogger')

        self.assertEqual(logger.name, 'testLogger')



if __name__ == "__main__":
    unittest.main()