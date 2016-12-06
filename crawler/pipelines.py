# -*- coding: utf-8 -*-
import requests
from crawler import BASE_PATH

from .items import CrawlItem, CrawlBulk
from .spiders import GenericMixin


class RESTPipeline(object):
    def __init__(self):
        self._token = None

    def process_item(self, item: CrawlItem, spider: GenericMixin):
        if not isinstance(item, CrawlItem):
            return item

        headers = {'Authorization-Token': spider.token, 'Content-Type': 'application/json'}
        requests.put('%s/%d/%s' % (BASE_PATH, item['source_id'], item['id']),
                     json=item._values,
                     headers=headers)
        return item


class BulkRESTPipeline(object):
    def __init__(self):
        self._token = None

    def process_item(self, bulk: CrawlBulk, spider: GenericMixin):
        if not isinstance(bulk, CrawlBulk):
            return bulk

        headers = {'Authorization-Token': spider.token, 'Content-Type': 'application/json'}
        requests.post('%s/' % BASE_PATH,
                      json=dict(activities=[item._values for item in bulk['bulk']]),
                      headers=headers)
        return bulk
