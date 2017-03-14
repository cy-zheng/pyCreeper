# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

class PycreeperException(Exception):
    """
    Base pycreeper exception.
    """

    def __init__(self, msg=None, stacktrace=None):
        self.msg = msg
        self.stacktrace = stacktrace

    def __str__(self):
        exception_msg = "Message: %s\n" % self.msg
        if self.stacktrace is not None:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += "Stacktrace:\n%s" % stacktrace
        return exception_msg


class TimeoutException(PycreeperException):
    pass
