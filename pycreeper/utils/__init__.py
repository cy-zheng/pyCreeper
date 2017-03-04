# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'


def result2list(result):
    """result to list
    """
    if result is None:
        return []
    if isinstance(result, (dict, basestring)):
        return [result]
    if hasattr(result, "__iter__"):
        return result


def call_func(func, errback=None, callback=None, *args, **kwargs):
    """执行某个函数,并自动包装异常和回调

    :param func:
    :param errback:
    :param callback:
    :param args:
    :param kwargs:
    """
    try:
        result = func(*args, **kwargs)
    except Exception as exc:
        if errback:
            errback(exc)
    else:
        if callback:
            result = callback(result)
        return result


def sorted_priority_dict(d):
    """Sort the priority dict to a ordered list.

    :param d: A priority dict.
    :return: Ordered list.
    """
    modules = sorted(d.items(), key=lambda x: x[1])
    modules = [x[0] for x in modules]
    return modules
