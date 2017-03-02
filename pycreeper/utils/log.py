# -*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'


import logging


def get_logger(settings, name='pyCreeperLogger'):
    """Create a Logger
    """
    log_level = getattr(logging, settings.get('LOG_LEVEL'), None)
    if not log_level:
        raise ValueError('Invaild LOG_LEVE. Please check your settings.py.')
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    stream = logging.StreamHandler()
    stream.setLevel(log_level)
    formatter = logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s")
    stream.setFormatter(formatter)
    logger.addHandler(stream)
    return logger
