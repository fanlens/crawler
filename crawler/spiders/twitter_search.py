#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Twitter API Spider"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union

from scrapy import Spider, Request

from common.utils.progress import ProgressCallbackBase
from common.utils.simple_utc import SimpleUTC
from . import GenericMixin, ProgressMixin
from .. import TSince
from ..items import CrawlItem, CrawlBulk
from ..middleware.twitter import TwitterSearchRequest, TwitterResponse


# todo include parent field
class TwitterSearchSpider(Spider, GenericMixin, ProgressMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "twitter"
    allowed_domains = ["twitter.com"]
    limits = {
        'search': 50,
    }

    def __init__(self,
                 source_id: int,
                 since: Optional[TSince] = None,
                 api_key: Optional[str] = None,
                 progress: Optional[ProgressCallbackBase] = None) -> None:
        """
        :param source_id: source id to crawl, must have type 'facebook'
        :param since: since when to crawl
        :param api_key: fanlens api key, will be deprecated
        :param progress: optional progress callback informing external systems
        """
        Spider.__init__(self, name=TwitterSearchSpider.name)
        GenericMixin.__init__(self, source_id=source_id, since=since, api_key=api_key)
        ProgressMixin.__init__(self, progress=progress)
        self.logger.info('crawling page %s since %s' % (self.source['slug'], self.since))

    def start_requests(self) -> List[Request]:
        """ :return: the initial Twitter API requests kicking off the crawling """
        return [TwitterSearchRequest(q=self.source['slug'])]

    def _create_item(self, data: Dict[str, Any]) -> CrawlItem:
        return CrawlItem(id=data['id_str'], source_id=self.source['id'], data=data,
                         crawl_ts=datetime.utcnow().replace(tzinfo=SimpleUTC()).isoformat())

    def parse(self, response: TwitterResponse) -> Union[Request, CrawlBulk]:
        """
        :param response: the Facebook page response
        :return: yielding created crawl items
        """
        if not response.tweets:
            raise StopIteration

        min_id = response.tweets[0]['id_str']
        self.logger.info('results for max_id: %s' % min_id)

        crawl_bulk = CrawlBulk(bulk=[])
        for tweet in response.tweets:
            created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
            if created_at < self.since:
                self.logger.info('hit historic cutoff %s with %s' % (str(self.since), str(created_at)))
                raise StopIteration
            crawl_bulk['bulk'].append(self._create_item(tweet))
        yield crawl_bulk

        max_id = response.tweets[-1]['id_str']
        yield TwitterSearchRequest(q=self.source['slug'], max_id=max_id)
