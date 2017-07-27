#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging, _get_handler
from scrapy.settings import Settings
import crawler.settings

from .spiders.facebook_page import FacebookPageSpider


def crawler_process(spider_class: object, **kwargs) -> CrawlerProcess:
    """
    returns a new crawler process for the provided spider type,
    call `start()` on the returned object to start the crawling process
    """
    crawler_settings = Settings()
    crawler_settings.setmodule(crawler.settings)  # get_project_settings doesn't work in this context!
    configure_logging(crawler_settings, install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('scrapy').addHandler(_get_handler(crawler_settings))
    # logging.getLogger('facebook').propagate = False
    # logging.getLogger('facebook').addHandler(_get_handler(crawler_settings))
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(spider_class, **kwargs)
    return process


def facebook_crawler_process(source_id, since=-14, api_key=None) -> CrawlerProcess:
    return crawler_process(FacebookPageSpider, source_id=source_id, since=since, api_key=api_key)
