#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Twitter Middleware"""

from typing import Any, Optional, Dict, List

import tweepy
from scrapy import Spider
from scrapy.http import Request, Response


# based on: https://github.com/yall/scrapy-twitter
# no license

# for other functionality revisit the original github


class TwitterStreamFilterRequest(Request):
    """Request adapter for track streams"""

    def __init__(self, *args: Any, track: str, **kwargs: Any) -> None:
        """
        :param track: the track keyword for the stream
        :param args: additional arguments for `Request`
        :param kwargs: additional keyword arguments for `Request`
        """
        self.track = track
        super(TwitterStreamFilterRequest, self).__init__('http://twitter.com', *args, dont_filter=True, **kwargs)


class TwitterSearchRequest(Request):
    # q is a twitter API parameter pylint: disable=invalid-name
    """Request adapter for search requests"""

    def __init__(self, *args: Any, q: str, max_id: Optional[str] = None, **kwargs: Any) -> None:
        """
        :param q: query string
        :param max_id: up to what tweet id to include results
        :param args: additional arguments for `Request`
        :param kwargs: additional keyword arguments for `Request`
        """
        self.q = q
        self.max_id = max_id
        super(TwitterSearchRequest, self).__init__('http://twitter.com', *args, dont_filter=True, **kwargs)


class TwitterResponse(Response):
    """Twitter `Response` adapter"""

    def __init__(self, *args: Any, tweets: List[Dict[str, Any]], **kwargs: Any) -> None:
        """
        :param tweets: the crawled tweets
        :param args: additional arguments for `Request`
        :param kwargs: additional keyword arguments for `Request`
        """
        self.tweets = tweets
        super(TwitterResponse, self).__init__('http://twitter.com', *args, **kwargs)


class TwitterDownloaderMiddleware(object):
    """Middleware for Twitter requests"""

    def __init__(self, consumer_key: str, consumer_secret: str,
                 access_token_key: str, access_token_secret: str) -> None:
        """
        :param consumer_key: Twitter consumer key
        :param consumer_secret: Twitter consumer secret
        :param access_token_key: Twitter access token key
        :param access_token_secret: Twitter access token secret
        """
        self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.auth.secure = True
        self.auth.set_access_token(access_token_key, access_token_secret)

        self.api = tweepy.API(self.auth,
                              wait_on_rate_limit=True,
                              wait_on_rate_limit_notify=True,
                              retry_count=5,
                              retry_delay=2)

    @classmethod
    def from_crawler(cls, crawler: Spider) -> 'TwitterDownloaderMiddleware':
        """
        :param crawler: the crawler to create the middleware from
        :return: a new middleware
        """
        settings = crawler.settings
        consumer_key = settings['TWITTER_CONSUMER_KEY']
        consumer_secret = settings['TWITTER_CONSUMER_SECRET']
        access_token_key = settings['TWITTER_ACCESS_TOKEN_KEY']
        access_token_secret = settings['TWITTER_ACCESS_TOKEN_SECRET']
        return cls(consumer_key,
                   consumer_secret,
                   access_token_key,
                   access_token_secret)

    def process_request(self, request: Request, spider: Spider) -> Optional[Response]:
        # conform to expected signature pylint: disable=unused-argument
        """
        :param request: incomming request, only specific instances of interest
        :param spider: spider the request belongs to
        :return: response for the Twitter request
        """
        if isinstance(request, TwitterSearchRequest):
            tweets = self.api.search(q=request.q,
                                     count=100,
                                     result_type='recent',
                                     include_entities=True,
                                     max_id=request.max_id)
            return TwitterResponse(tweets=[tweet._json for tweet in tweets])  # pylint: disable=protected-access

        # if isinstance(request, TwitterStreamFilterRequest):
        #     tweets = self.api.GetStreamFilter(track=request.track)
        #     return TwitterResponse(tweets=tweets)

        return None

    def process_response(self, request: Request, response: Response, spider: Spider) -> Response:
        # conform to expected signature pylint: disable=unused-argument, no-self-use
        """unused"""
        return response
