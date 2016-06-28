# -*- coding: utf-8 -*-
import datetime
import logging

from db import DB, insert_or_ignore
from db.models.facebook import FacebookPostEntry, FacebookCommentEntry, FacebookReactionEntry
from .items import FacebookItem


class StoreFacebookPipeline(object):
    item_cls = {
        'post': FacebookPostEntry,
        'comments': FacebookCommentEntry,
        'reactions': FacebookReactionEntry,
    }

    def __init__(self):
        self.session = None
        self.max_dangling = 500
        self.dangling = 0
        self.crawl_ts = 0
        self.buffer = []
        self.db = DB()

    def open_spider(self, spider):
        logging.info('open storefacebook pipeline')
        self.crawl_ts = datetime.datetime.utcnow()
        self.dangling = 0
        self.session = self.db.session

    def close_spider(self, spider):
        logging.info('closing storefacebook pipeline')
        self.session.commit()
        self.session.close()

    def process_item(self, item: FacebookItem, spider):
        item_type = item['type']
        item_cls = self.item_cls[item_type]
        entry = item_cls(id=item['id'], data=item['data'], crawl_ts=self.crawl_ts, meta=item['meta'])
        if 'post_id' in item['meta']:
            entry.post_id = item['meta']['post_id']
            del entry.meta['post_id']  # no need to store twice
        # insert_or_update(self.session, entry, 'id', update_fields={'crawl_ts'})
        insert_or_ignore(self.session, entry)
        self.dangling += 1
        if self.dangling > self.max_dangling:
            logging.debug("committing to db")
            self.session.commit()
            self.dangling = 0
        return item
