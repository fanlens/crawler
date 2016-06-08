#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from scrapy.crawler import CrawlerProcess, configure_logging
from scrapy.utils.log import configure_logging, _get_handler
from scrapy.utils.project import get_project_settings

from crawler.spiders.facebook_page import FacebookPageSpider


def facebook_page_process(page, since=None, include_extensions=None, progress=None) -> CrawlerProcess:
    """
    returns a new crawler process for the facebook page spider,
    call `start()` on the returned object to start the crawling process
    """
    configure_logging(get_project_settings(), install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('scrapy').addHandler(_get_handler(get_project_settings()))
    logging.getLogger('facebook').propagate = False
    logging.getLogger('facebook').addHandler(_get_handler(get_project_settings()))
    process = CrawlerProcess(get_project_settings())
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
