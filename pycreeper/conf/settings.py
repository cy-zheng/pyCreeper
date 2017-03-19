# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

"""" Settings """

import json
from importlib import import_module

from pycreeper.conf import default_settings


class Settings(object):
    """ Settings Object """

    def __init__(self, values=None):
        self.attrs = {}
        self.load_config(default_settings)
        if values:
            self.load_config(values)

    def __getitem__(self, key):
        """__getitem__

        @key, str, key
        """
        return self.attrs[key] if key in self.attrs else None

    def load_config(self, module):
        """load config

        @module, module
        """
        if isinstance(module, basestring):
            module = import_module(module)
        for key in module if isinstance(module, dict) else dir(module):
            if key.isupper():
                self.set(key, module.get(key) \
                    if isinstance(module, dict) else getattr(module, key))

    def set(self, key, value):
        """set

        @key, str, key
        @value, str/int/float value
        """
        self.attrs[key] = value

    def set_dict(self, values):
        """set dict

        @values, dict, values
        """
        for key, value in values.iteritems():
            self.set(key, value)

    def get(self, key, default=None):
        """get

        @key, str, key
        @default, default
        """
        return self[key] or default

    def get_int(self, key, default=0):
        """get int

        @key, str, key
        @default, int
        """
        return int(self.get(key, default))

    def get_float(self, key, default=0.0):
        """get float

        @key, str, key
        @default, float
        """
        return float(self.get(key, default))

    def get_list(self, key, default=None):
        """get list

        @key, str, key
        @default, list
        """
        value = self.get(key, default or None)
        if isinstance(value, basestring):
            value = value.split(",")
        return value

    def get_dict(self, key, default=None):
        """get dict

        @key, str, key
        @default, dict
        """
        value = self.get(key, default or None)
        if isinstance(value, basestring):
            value = json.loads(value)
        return value
