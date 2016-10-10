#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dateutil.parser

from config.db import Config

_CONFIG = Config("facebook")
GRAPH_URL = 'https://graph.facebook.com/v2.6'


def with_access_token(fun):
    def wrapped(*args, **kwargs):
        url = fun(*args, **kwargs)
        if '?' not in url:
            url += '?'
        url += '&access_token=' + str(_CONFIG['access_token'])
        return url

    return wrapped


@with_access_token
def page_url(page, limit=100, since=None):
    url = GRAPH_URL + '/%s/feed?limit=%d' % (page, limit)
    if since is not None:
        if isinstance(since, str):
            url += '&since=' + dateutil.parser.parse(since).strftime("%s")
        else:
            url += '&since=' + str(since)
    return url


@with_access_token
def extension_url(post_id, extension, limit=2000, since=None):
    url = GRAPH_URL + '/%s/%s?order=reverse_chronological&limit=%d' % (post_id, extension, limit)
    if since is not None:
        if isinstance(since, str):
            url += '&since=' + dateutil.parser.parse(since).strftime("%s")
        else:
            url += '&since=' + str(since)
    return url
