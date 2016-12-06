#!/usr/bin/env python
# -*- coding: utf-8 -*-
import dateutil.parser

GRAPH_URL = 'https://graph.facebook.com/v2.6'


def with_access_token(crawler, url):
    if '?' not in url:
        url += '?'
    url += '&access_token=' + crawler.settings['FACEBOOK_ACCESS_TOKEN']
    return url


def page_url(crawler, page, limit=100, since=None):
    url = GRAPH_URL + '/%s/feed?limit=%d' % (page, limit)
    if since is not None:
        if isinstance(since, str):
            url += '&since=' + dateutil.parser.parse(since).strftime("%s")
        else:
            url += '&since=' + str(since)
    return with_access_token(crawler, url)


def extension_url(crawler, post_id, extension, limit=2000, since=None):
    url = GRAPH_URL + '/%s/%s?order=reverse_chronological&limit=%d' % (post_id, extension, limit)
    if since is not None:
        if isinstance(since, str):
            url += '&since=' + dateutil.parser.parse(since).strftime("%s")
        else:
            url += '&since=' + str(since)
    return with_access_token(access_token, url)
