#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging, _get_handler
from scrapy.settings import Settings
from . import settings

from crawler.spiders.facebook_page import FacebookPageSpider


def facebook_page_process(page, since=None, include_extensions=None, progress=None) -> CrawlerProcess:
    """
    returns a new crawler process for the facebook page spider,
    call `start()` on the returned object to start the crawling process
    """
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    configure_logging(crawler_settings, install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('scrapy').addHandler(_get_handler(crawler_settings))
    logging.getLogger('facebook').propagate = False
    logging.getLogger('facebook').addHandler(_get_handler(crawler_settings))
    process = CrawlerProcess(settings=crawler_settings)
    # todo ugly/stupid
    kwargs = dict(page=page)
    if since is not None:
        kwargs['since'] = since
    if include_extensions is not None:
        kwargs['include_extensions'] = include_extensions
    if progress is not None:
        kwargs['progress'] = progress
    process.crawl(FacebookPageSpider, **kwargs)
    return process
