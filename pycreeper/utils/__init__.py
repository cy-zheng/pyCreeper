# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import six

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


def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object `text`. If `text`
    is already an unicode object, return it as-is."""
    if isinstance(text, six.text_type):
        return text
    if not isinstance(text, (bytes, six.text_type)):
        raise TypeError('to_unicode must receive a bytes, str or unicode '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)


def to_bytes(text, encoding=None, errors='strict'):
    """Return the binary representation of `text`. If `text`
    is already a bytes object, return it as-is."""
    if isinstance(text, bytes):
        return text
    if not isinstance(text, six.string_types):
        raise TypeError('to_bytes must receive a unicode, str or bytes '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.encode(encoding, errors)


def to_native_str(text, encoding=None, errors='strict'):
    """ Return str representation of `text`
    (bytes in Python 2.x and unicode in Python 3.x). """
    if six.PY2:
        return to_bytes(text, encoding, errors)
    else:
        return to_unicode(text, encoding, errors)
