# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import typing
import scrapy


class CrawlItem(scrapy.Item):
    id = scrapy.Field()
    source_id = scrapy.Field()
    data = scrapy.Field()
    crawl_ts = scrapy.Field()


class CrawlBulk(scrapy.Item):
    bulk = scrapy.Field()  # type: typing.List[CrawlItem]
