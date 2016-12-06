#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from datetime import datetime, tzinfo, timedelta

from crawler.spiders import GenericMixin, ProgressMixin
from crawler.items import CrawlItem, CrawlBulk
from crawler.middleware.twitter import TwitterSearchRequest, TwitterResponse


class simple_utc(tzinfo):
    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


# todo include parent field
class TwitterSearchSpider(scrapy.Spider, GenericMixin, ProgressMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "twitter"
    allowed_domains = ["twitter.com"]
    limits = {
        'search': 50,
    }

    def __init__(self, source_id, since=None, token=None, progress=None):
        GenericMixin.__init__(self, source_id=source_id, since=since, token=token)
        ProgressMixin.__init__(self, progress=progress)
        self.logger.info('crawling page %s since %s' % (self.source['slug'], self.since))

    def start_requests(self):
        return [TwitterSearchRequest(q=self.source['slug'])]

    def _create_item(self, data: dict) -> CrawlItem:
        return CrawlItem(id=data['id_str'], source_id=self.source['id'], data=data,
                         crawl_ts=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())

    def parse(self, response: TwitterResponse):
        if not response.tweets:
            raise StopIteration

        min_id = response.tweets[0]['id_str']
        self.logger.info('results for max_id: %s' % min_id)

        crawl_bulk = CrawlBulk(bulk=[])
        for tweet in response.tweets:
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if created_at < self.since_dt:
                self.logger.info('hit historic cutoff %s with %s' % (str(self.since_dt), str(created_at)))
                raise StopIteration
            crawl_bulk['bulk'].append(self._create_item(tweet))
        yield crawl_bulk

        max_id = response.tweets[-1]['id_str']
        yield TwitterSearchRequest(q=self.source['slug'], max_id=max_id)
