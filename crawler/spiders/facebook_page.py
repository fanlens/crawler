#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Facebook API Spider"""
from datetime import datetime
from typing import Optional, Dict, Any, Union, Set

from scrapy import Spider
from scrapy.http import Request, Response

from common.utils.progress import ProgressCallbackBase
from common.utils.simple_utc import SimpleUTC
from . import GenericMixin, ProgressMixin, parse_json
from .. import TSince
from ..api.facebook import extension_url, page_feed_url, Extension
from ..items import CrawlItem, CrawlBulk


class FacebookPageSpider(Spider, GenericMixin, ProgressMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "facebook"
    allowed_domains = ["facebook.com"]
    allowed_extensions = {Extension.comments.value, Extension.reactions.value}
    limits = {
        'post': 50,
        Extension.comments: 700,
        Extension.reactions: 4000
    }

    def __init__(self,  # pylint: disable=too-many-arguments
                 source_id: int,
                 since: Optional[TSince] = None,
                 include_extensions: str = 'comments',
                 api_key: Optional[str] = None,
                 progress: Optional[ProgressCallbackBase] = None) -> None:
        """
        :param source_id: source id to crawl, must have type 'facebook'
        :param since: since when to crawl
        :param include_extensions: which extensions to include (comments, reactions) as csv string
        :param api_key: fanlens api key, will be deprecated
        :param progress: optional progress callback informing external systems
        """
        Spider.__init__(self, FacebookPageSpider.name)
        GenericMixin.__init__(self, source_id=source_id, since=since, api_key=api_key)
        ProgressMixin.__init__(self, progress=progress)
        self.start_urls = [page_feed_url(self.source['slug'], limit=self.limits['post'], since=self.since)]
        self.logger.info('Crawling page %s since %s' % (self.source['slug'], self.since))
        self._included_extensions = {Extension[extension_str] for extension_str in
                                     set(include_extensions.lower().split(',')).intersection(self.allowed_extensions)}

    def _create_item(self, data: Dict[str, Any]) -> CrawlItem:
        return CrawlItem(id=data['id'], source_id=self.source['id'], data=data,
                         crawl_ts=datetime.utcnow().replace(tzinfo=SimpleUTC()).isoformat())

    def parse(self, response: Response) -> Union[CrawlItem, Request]:
        """
        :param response: the Facebook page response
        :return: yielding created crawl items
        """
        json_body = parse_json(response)
        self.logger.info(response.url)
        for post in json_body['data']:
            self.send_progress(post_id=post['id'], post_date=post['created_time'], since=self.since)
            if post.get('message') and post.get('from'):
                yield self._create_item(post)
                continue
            for extension in self.included_extensions:
                request = Request(extension_url(post['id'], extension, limit=self.limits[extension]),
                                  callback=self.parse_extension)
                yield request
            if 'next' in json_body.get('paging', ()):
                yield Request(json_body['paging']['next'], callback=self.parse)

    def parse_extension(self, response: Response) -> Union[CrawlBulk, Request]:
        """
        :param response: the Facebook extension response
        :return: yielding created crawl item bulks
        """
        json_body = parse_json(response)
        bulk_size = 5
        for i in range(0, len(json_body['data']), bulk_size):
            crawl_bulk = CrawlBulk(bulk=[self._create_item(extension) for extension in json_body['data'][i:bulk_size]
                                         if extension.get('message') and extension.get('from')])
            yield crawl_bulk
        if 'next' in json_body.get('paging', ()):
            paging_request = Request(json_body['paging']['next'], callback=self.parse_extension)
            paging_request.meta.update(response.meta)
            yield paging_request

    @property
    def included_extensions(self) -> Set[Extension]:
        """:return: Extensions that will be crawled for the page's posts"""
        return self._included_extensions
