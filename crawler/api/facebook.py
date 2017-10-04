#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper methods to access Facebook api"""
from datetime import datetime
from enum import Enum
from typing import Optional

import dateutil.parser

from .. import TSince
from ..settings import FACEBOOK_ACCESS_TOKEN

GRAPH_URL = 'https://graph.facebook.com/v2.6'


def with_access_token(url: str, token: Optional[str] = None) -> str:
    """
    Add access token query parameter to Facebook url
    :param url: the Facebook url to wrap
    :param token: the access token to use, default: systen access token
    :return: Facebook url with proper access token parameter
    """
    if '?' not in url:
        url += '?'
    return url + '&access_token=' + (token or FACEBOOK_ACCESS_TOKEN)


def with_since(url: str, since: Optional[TSince]) -> str:
    """
    Add a since parameter to the Facebook url
    :param url: the Facebook url to wrap
    :param since: the timestamp to use, can be parseable string, unix timestamp or datetime instance
    :return: Facebook url with proper access since parameter
    :raises ValueError: if since is in wrong timestamp format
    """
    if not since:
        return url
    if isinstance(since, datetime):
        since_datetime = since
    elif isinstance(since, int):
        since_datetime = datetime.fromtimestamp(since)  # no UTC
    elif isinstance(since, str):
        since_datetime = dateutil.parser.parse(since)
    else:
        raise ValueError("since parameter is in an unsupported format")
    if '?' not in url:
        url += '?'
    return url + '&since=' + since_datetime.strftime("%s")


def page_feed_url(page: str, limit: int = 100, since: Optional[TSince] = None, token: str = '') -> str:
    """
    :param page: the Facebook page to get the feed URL for
    :param limit: amount of posts to include in feed
    :param since: posts since timestamp. can be parseable string, unix timestamp or datetime instance
    :param token: the access_token to use, default system access token
    :return: Facebook API URL for the page feed
    """
    url = GRAPH_URL + '/%s/feed?limit=%d' % (page, limit)
    url = with_since(url, since)
    return with_access_token(url, token)


class Extension(Enum):
    """Allowed extensions for Facebook posts"""
    comments = "comments"
    reactions = "reactions"
    likes = "likes"


def extension_url(post_id: str,
                  extension: Extension,
                  limit: int = 2000,
                  since: Optional[TSince] = None,
                  token: Optional[str] = None) -> str:
    """
    :param post_id: id of Facebook post to get the extension for
    :param extension: comment, likes, reactions
    :param limit: amount of extensions to include
    :param since: extensions since timestamp
    :param token: the access_token to use, default system access token
    :return: Facebook API URL for the extensions
    :raises ValueError: if extension is not allowed
    """
    if extension not in ('comment', 'likes', 'reactions'):
        raise ValueError("Unrecognized extension used")
    url = GRAPH_URL + '/%s/%s?order=reverse_chronological&limit=%d' % (post_id, extension.value, limit)
    url = with_since(url, since)
    return with_access_token(url, token)
