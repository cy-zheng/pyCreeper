# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import gevent


def spawn(func, *args, **kwargs):
    return gevent.spawn(func, *args, **kwargs)


def join_all(funcs):
    gevent.joinall(funcs)
