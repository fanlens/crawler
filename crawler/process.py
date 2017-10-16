"""Tools to embed the scrapy crawler as a subprocess."""

from typing import Type, Any, Union, Optional
from warnings import warn
import logging

from datetime import datetime
from scrapy import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from scrapy.utils.log import configure_logging, _get_handler

from . import settings
from .spiders.facebook_page import FacebookPageSpider


def crawler_process(spider_class: Type[Spider], **kwargs: Any) -> CrawlerProcess:
    """
    returns a new crawler process for the provided spider type,
    call `start()` on the returned object to start the crawling process
    :param spider_class: the crawler class to instantiate
    """
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)  # get_project_settings doesn't work in this context!
    configure_logging(crawler_settings, install_root_handler=False)
    logging.getLogger('scrapy').propagate = False
    logging.getLogger('scrapy').addHandler(_get_handler(crawler_settings))
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(spider_class, **kwargs)
    return process


def facebook_crawler_process(source_id: int,
                             since: Optional[Union[int, datetime]] = -14,
                             api_key: Optional[str] = None) -> CrawlerProcess:
    """
    Factory method to create a Facebook crawler sub process.
    :param source_id: id of the source to crawl, must be type facebook
    :param since: since when to crawl, default -14 days. Can be a epoch timestamp,
        a negative integer specifying a delta in days (e.g. -14 for -14 days), or a datetime instance
    :param api_key: fanlens api key if REST pipeline is used
    :return: embeddable facebook crawling sub process
    """
    if api_key:
        warn('Use the database pipeline.', PendingDeprecationWarning)
    return crawler_process(FacebookPageSpider, source_id=source_id, since=since, api_key=api_key)
