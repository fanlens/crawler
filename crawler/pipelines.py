#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Pipelines for crawled items"""
import requests
from scrapy import Item

from common.db import get_session, Session, insert_or_ignore
from common.db.models.activities import Data
from . import api_path, headers
from .items import CrawlItem, CrawlBulk
from .spiders import GenericMixin


# pylint: disable=too-few-public-methods, no-self-use

class RESTPipeline(object):
    """REST based pipeline for a single `CrawlItem`"""

    def process_item(self, item: CrawlItem, spider: GenericMixin) -> Item:
        """
        Process a single `CrawlItem` if there is an api_key present in the spider
        :param item: the crawled item
        :param spider: the spider
        :return: the item for further processing
        """
        if not isinstance(item, CrawlItem) or spider.api_key is None:
            return item

        requests.put(api_path(item['source_id'], item['id']),
                     json=item._values,  # pylint: disable=protected-access
                     headers=headers(spider.api_key))
        return item


class BulkRESTPipeline(object):
    """REST based pipeline for a `CrawlBulk`"""

    def process_item(self, bulk: CrawlBulk, spider: GenericMixin) -> Item:
        """
        Process a `CrawlBulk` if there is an api_key present in the spider
        :param bulk: the bulk of crawled items
        :param spider: the spider
        :return: the item for further processing
        """
        if not isinstance(bulk, CrawlBulk) or spider.api_key is None:
            return bulk
        if not bulk['bulk']:
            return bulk

        requests.post(api_path(),
                      json=dict(activities=[item._values for item in bulk['bulk']]),  # pylint: disable=protected-access
                      headers=headers(spider.api_key))
        return bulk


class DBPipeline(object):
    """DB based pipeline for a single `CrawlItem`"""

    @staticmethod
    def insert_item_db(session: Session, item: CrawlItem) -> Item:
        """
        Inserts the crawl item as `Data` item into the DB. Ignores duplicate entries.
        :param session: database session to use
        :param item: the crawled item
        """
        insert_or_ignore(session,
                         Data(source_id=item['source_id'],
                              object_id=item['id'],
                              data=item['data'],
                              crawled_ts=item['crawl_ts']))

    def process_item(self, item: CrawlItem, spider: GenericMixin) -> Item:
        """
        Process a single `CrawlItem` if there is no api_key present in the spider
        :param item: the crawled item
        :param spider: the spider
        :return: the item for further processing
        """
        if not isinstance(item, CrawlItem) or spider.api_key is not None:
            return item
        with get_session() as session:
            self.insert_item_db(session, item)
            session.commit()


class BulkDBPipeline(object):
    """DB based pipeline for a `CrawlBulk`"""

    def process_item(self, bulk: CrawlBulk, spider: GenericMixin) -> Item:
        """
        Process a `CrawlBulk` if there is no api_key present in the spider
        :param bulk: the bulk of crawled items
        :param spider: the spider
        :return: the item for further processing
        """
        if not isinstance(bulk, CrawlBulk) or spider.api_key is not None:
            return bulk
        with get_session() as session:
            for item in bulk['bulk']:
                DBPipeline.insert_item_db(session, item)
            session.commit()
