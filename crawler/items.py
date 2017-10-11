#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Defined  models for scraped items"""
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import typing

import scrapy


# pylint: disable=too-many-ancestors

class CrawlItem(scrapy.Item):
    """A generic data object carrying the raw data in json"""
    id = scrapy.Field()  # pylint: disable=invalid-name
    source_id = scrapy.Field()
    data = scrapy.Field()
    crawl_ts = scrapy.Field()


class CrawlBulk(scrapy.Item):
    """A bulk of `CrawlItem`"""
    bulk: typing.List[CrawlItem] = scrapy.Field()
