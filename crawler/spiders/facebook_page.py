#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from crawler.spiders import GenericMixin, ProgressMixin
from crawler.api.facebook import extension_url, page_url
from crawler.items import CrawlItem, CrawlBulk
from crawler.spiders import parse_json

from datetime import datetime, tzinfo, timedelta


class simple_utc(tzinfo):
    def tzname(self):
        return "UTC"

    def utcoffset(self, dt):
        return timedelta(0)


# todo include parent field
class FacebookPageSpider(scrapy.Spider, GenericMixin, ProgressMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "facebook"
    allowed_domains = ["facebook.com"]
    allowed_extensions = {'comments', 'reactions'}
    limits = {
        'post': 50,
        'comments': 700,
        'reactions': 4000
    }

    def __init__(self, user_id, source_id, since=None, include_extensions='comments', token=None, progress=None):
        GenericMixin.__init__(self, user_id=user_id, source_id=source_id, since=since, token=token)
        ProgressMixin.__init__(self, progress=progress)
        self.start_urls = [page_url(self.source.slug, limit=self.limits['post'], since=self.since)]
        self.logger.info('crawling page %s since %s' % (self.source.slug, self.since))
        self._included_extensions = set(include_extensions.lower().split(',')).intersection(self.allowed_extensions)

    def _create_item(self, data):
        return CrawlItem(id=data['id'], source_id=self.source.id, data=data,
                         crawl_ts=datetime.utcnow().replace(tzinfo=simple_utc()).isoformat())

    @parse_json
    def parse(self, response, json_body=None):
        self.logger.info(response.url)
        for post in json_body['data']:
            self.send_progress(post_id=post['id'], post_date=post['created_time'], since=self.since)
            yield self._create_item(post)
            for extension in self.included_extensions:
                request = scrapy.Request(extension_url(post['id'], extension, limit=self.limits[extension]),
                                         callback=self.parse_extension)
                yield request
            if 'next' in json_body.get('paging', ()):
                yield scrapy.Request(json_body['paging']['next'], callback=self.parse)

    @parse_json
    def parse_extension(self, response, json_body=None):
        crawl_bulk = CrawlBulk(bulk=[self._create_item(extension) for extension in json_body['data']])
        yield crawl_bulk
        if 'next' in json_body.get('paging', ()):
            paging_request = scrapy.Request(json_body['paging']['next'], callback=self.parse_extension)
            paging_request.meta.update(response.meta)
            yield paging_request

    @property
    def included_extensions(self) -> set:
        return self._included_extensions
