#-*- coding:utf-8 -*-
reload(__import__('sys')).setdefaultencoding('utf-8')
__author__ = 'zcy'

import urllib
from urlparse import parse_qsl, urlparse, urlunparse
import hashlib


def request_fingerprint(request):
    """request fingerprint
    """
    scheme, netloc, path, params, query, fragment = urlparse(request.url)
    keyvals = parse_qsl(query)
    keyvals.sort()
    query = urllib.urlencode(keyvals)
    canonicalize_url = urlunparse((
        scheme, netloc.lower(), path, params, query, fragment))
    fpr = hashlib.sha1()
    fpr.update(canonicalize_url)
    return fpr.hexdigest()