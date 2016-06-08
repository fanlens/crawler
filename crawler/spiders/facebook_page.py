#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrapy

from db.models.facebook import FacebookPostEntry
from crawler.spiders import FacebookMixin, ProgressMixin
from crawler.api.facebook import extension_url, page_url
from crawler.items import FacebookItem
from crawler.spiders import parse_json


class FacebookPageSpider(scrapy.Spider, FacebookMixin, ProgressMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "facebook"
    allowed_domains = ["facebook.com"]
    allowed_extensions = set(['comments', 'reactions'])

    def __init__(self, page='', since=None, include_extensions='comments,reactions', progress=None):
        FacebookMixin.__init__(self, page=page, since=since, root_model=FacebookPostEntry)
        ProgressMixin.__init__(self, progress=progress)
        self.start_urls = [page_url(page, limit=self.limits['post'], since=self.since)]
        self.logger.info('crawling page %s since %s' % (self.page, self.since))
        self._included_extensions = set(include_extensions.lower().split(',')).intersection(self.allowed_extensions)

    @parse_json
    def parse(self, response, json_body=None):
        self.logger.info(response.url)
        for post in json_body['data']:
            self.send_progress(post_id=post['id'], post_date=post['created_time'], since=self.since)
            yield FacebookItem(id=post['id'], type='post', data=post, meta=dict(page=self.page))
            for extension in self.included_extensions:
                request = scrapy.Request(extension_url(post['id'], extension, limit=self.limits[extension]),
                                         callback=self.parse_extension)
                request.meta['post_id'] = post['id']
                request.meta['extension'] = extension
                yield request
            if 'next' in json_body.get('paging', ()):
                yield scrapy.Request(json_body['paging']['next'], callback=self.parse)

    @parse_json
    def parse_extension(self, response, json_body=None):
        for extension in json_body['data']:
            yield FacebookItem(id=extension['id'], type=response.meta['extension'],
                               data=extension, meta=dict(post_id=response.meta['post_id'], page=self.page))
        if 'next' in json_body.get('paging', ()):
            paging_request = scrapy.Request(json_body['paging']['next'], callback=self.parse_extension)
            paging_request.meta.update(response.meta)
            yield paging_request

    @property
    def included_extensions(self) -> set:
        return self._included_extensions
