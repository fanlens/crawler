# -*- coding: utf-8 -*-
import requests
from crawler import api_path, headers
from db.models.activities import Data
from db import get_session, insert_or_ignore

from .items import CrawlItem, CrawlBulk
from .spiders import GenericMixin


class RESTPipeline(object):
    def process_item(self, item: CrawlItem, spider: GenericMixin):
        if not isinstance(item, CrawlItem) or spider.api_key is None:
            return item

        requests.put(api_path(item['source_id'], item['id']),
                     json=item._values,
                     headers=headers(spider.api_key))
        return item


class BulkRESTPipeline(object):
    def process_item(self, bulk: CrawlBulk, spider: GenericMixin):
        if not isinstance(bulk, CrawlBulk) or spider.api_key is None:
            return bulk
        if len(bulk['bulk']) == 0:
            return bulk

        requests.post(api_path(),
                      json=dict(activities=[item._values for item in bulk['bulk']]),
                      headers=headers(spider.api_key))
        return bulk


class DBPipeline(object):
    @staticmethod
    def insert_item_db(session, item: CrawlItem):
        insert_or_ignore(session,
                         Data(source_id=item['source_id'],
                              object_id=item['id'],
                              data=item['data'],
                              crawled_ts=item['crawl_ts']))

    def process_item(self, item: CrawlItem, spider: GenericMixin):
        if not isinstance(item, CrawlItem) or spider.api_key is not None:
            return item
        with get_session() as session:
            self.insert_item_db(session, item)
            session.commit()


class BulkDBPipeline(object):
    def process_item(self, bulk: CrawlBulk, spider: GenericMixin):
        if not isinstance(bulk, CrawlBulk) or spider.api_key is not None:
            return bulk
        with get_session() as session:
            for item in bulk['bulk']:
                DBPipeline.insert_item_db(session, item)
            session.commit()
