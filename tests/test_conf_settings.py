# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import unittest

from pycreeper.conf.settings import Settings
from tests.test_data import test_settings_data

CONF_PATH = 'tests.test_data.test_settings_data'


class SettingsTest(unittest.TestCase):
    def test_basics(self):
        settings = Settings()
        self.assertEqual(settings['RETRY_COUNT'], 3)
        settings = Settings(test_settings_data)
        self.assertEqual(settings['TEST_INT'], 10)

    def test_get_item(self):
        settings = Settings(test_settings_data)
        self.assertEqual(settings['TEST_STR'], 'foo,bar,baz')
        self.assertEqual(settings['TEST_DICT'], {"foo": "bar"})

    def test_load_config(self):
        settings = Settings(test_settings_data)
        self.assertEqual(settings['TEST_STR'], 'foo,bar,baz')
        settings = Settings(CONF_PATH)
        self.assertEqual(settings['TEST_STR'], 'foo,bar,baz')
        self.assertRaises(KeyError, settings['test_lowcase'])

    def test_set(self):
        settings = Settings(test_settings_data)
        self.assertRaises(KeyError, settings['TEST_SET'])
        settings.set('TEST_SET', True)
        self.assertEqual(settings['TEST_SET'], True)

    def test_set_dict(self):
        settings = Settings(test_settings_data)
        self.assertRaises(KeyError, settings['TEST_SET_1'])
        self.assertRaises(KeyError, settings['TEST_SET_2'])
        settings.set_dict(
            {
                'TEST_SET_1': True,
                'TEST_SET_2': False
            }
        )
        self.assertEqual(settings['TEST_SET_1'], True)
        self.assertEqual(settings['TEST_SET_2'], False)

    def test_get(self):
        settings = Settings(test_settings_data)
        self.assertEqual(settings.get('TEST_GET'), None)
        self.assertEqual(settings.get('TEST_GET', 'foo'), 'foo')
        settings.set('TEST_GET', 'bar')
        self.assertEqual(settings.get('TEST_GET', 'foo'), 'bar')

    def test_get_int_and_float(self):
        settings = Settings(test_settings_data)
        self.assertIsInstance(settings.get_float('TEST_INT'), float)
        self.assertIsInstance(settings.get_int('TEST_FLOAT'), int)

    def test_get_list(self):
        settings = Settings(test_settings_data)
        self.assertIsInstance(settings.get_list('TEST_LIST'), list)
        self.assertIsInstance(settings.get_list('TEST_STR'), list)

    def test_get_dict(self):
        settings = Settings(test_settings_data)
        self.assertIsInstance(settings.get_dict('TEST_DICT'), dict)
        self.assertIsInstance(settings.get_dict('TEST_JSON'), dict)


if __name__ == "__main__":
    unittest.main()
