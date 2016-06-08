#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" a crawler that does smart refetching... intended for later! atm just refetch the whole page"""

import dateutil.parser
import scrapy
from sqlalchemy import text

from db import DB
from crawler.spiders import FacebookMixin
from crawler.api.facebook import extension_url
from crawler.items import FacebookItem
from crawler.spiders import parse_json


class FacebookExtensionsSpider(scrapy.Spider, FacebookMixin):
    """Spider that crawls the posts, their comments and reactions for the specified page """
    name = "facebook_extensions"

    interval = property(lambda self: 30 * 60 * 1000)
    scaling = property(lambda self: 10)
    chance = property(lambda self: 0.01)

    # max_run_ts + (interval / #elements_last_run / #intervals / scalingfactor(100comments/interval = 1 -> 100)
    _refetch_sql_raw = """
WITH
    NOW_EPOCH AS (
      SELECT (EXTRACT(EPOCH FROM now()) * 1000) :: BIGINT AS ms),
    MAX_RUN_TS AS (
      SELECT
        post_id,
        max(crawl_ts) AS max_crawl_ts
      FROM %(extensions_table)s
      WHERE meta :: JSONB ->> 'page' = :page
      GROUP BY post_id),
    CUR_RUN AS (
      SELECT
        extensions.post_id AS post_id,
        count(*)           AS num_ext,
        max_crawl_ts
      FROM %(extensions_table)s AS extensions
        JOIN MAX_RUN_TS ON extensions.post_id = MAX_RUN_TS.post_id
      WHERE extensions.crawl_ts = max_crawl_ts
      GROUP BY extensions.post_id, max_crawl_ts),
    INPUTVARS AS (
      SELECT
        posts.id                                                                         AS post_id,
        COALESCE(
            extract(EPOCH FROM CUR_RUN.max_crawl_ts) :: BIGINT * 1000,
            extract(EPOCH FROM posts.crawl_ts) :: BIGINT * 1000) :: BIGINT               AS max_crawl_ts,
        EXTRACT(EPOCH FROM COALESCE(
            max(extensions.data :: JSONB ->> 'created_time'),
            posts.data ->> 'created_time') :: TIMESTAMP WITH TIME ZONE) :: BIGINT * 1000 AS max_ts,
        num_ext
      FROM (data.facebook_posts AS posts LEFT OUTER JOIN %(extensions_table)s AS extensions
          ON posts.id = extensions.post_id) JOIN CUR_RUN ON posts.id = CUR_RUN.post_id
      GROUP BY posts.id, num_ext, CUR_RUN.max_crawl_ts)
SELECT
  post_id,
  max_ts
FROM INPUTVARS, NOW_EPOCH
WHERE
  max_crawl_ts +
  (:interval :: FLOAT /
   greatest(nullif(num_ext :: FLOAT, 0) /
            greatest((nullif(coalesce(:now, ms) - max_ts, 0) :: FLOAT /
                      :interval) :: FLOAT, 1) /
            :scaling, 0.0001)) < coalesce(:now, ms)
  OR random() < :chance"""

    def __init__(self, extension, page='', since=None, progress=None):
        assert extension in self.root_models
        self._extension = extension
        FacebookMixin.__init__(self, page=page, since=since, root_model=self.root_model)
        ProgressMixin.__init__(self, progress=progress)
        self.logger.info('crawling extension %s for page %s since %s' % (self.extension, self.page, self.since))

    def _with_extions_table(self, sql_raw):
        extensions_table = '%s.%s' % (self.root_model.__table__.schema, self.root_model.__table__.name)
        return text(sql_raw % dict(extensions_table=extensions_table))

    def start_requests(self):
        with DB().ctx() as session:
            to_refetch = session.execute(self._with_extions_table(self._refetch_sql_raw),
                                         params=dict(page=self.page,
                                                     now=None,
                                                     scaling=self.scaling,
                                                     chance=self.chance,
                                                     interval=self.interval))
            for (post_id, max_ts) in to_refetch:
                start_request = scrapy.Request(
                    extension_url(post_id, self.extension,
                                  limit=self.limits[self.extension],
                                  since=max_ts),
                    callback=self.parse)
                start_request.meta['post_id'] = post_id
                start_request.meta['max_ts'] = max_ts
                yield start_request
            raise StopIteration

    @parse_json
    def parse(self, response, json_body=None):
        stop_paging = False
        for extension in json_body['data']:
            # todo optimize: reactions only have ids so i'll have to search for an id instead of a generic timestamp :(
            created_time = extension.get('created_time', '1970-01-01T00:00:00+0000')
            stop_paging = int(dateutil.parser.parse(created_time).strftime("%s")) <= response.meta['max_ts']
            yield FacebookItem(id=extension['id'], type=self.extension, data=extension,
                               meta=dict(page=self.page, post_id=response.meta['post_id']))

        if 'next' in json_body.get('paging', ()) and not stop_paging:
            paging_request = scrapy.Request(json_body['paging']['next'], callback=self.parse)
            paging_request.meta.update(response.meta)
            yield paging_request
        else:
            self.logger.debug('found time horizon (%s), stop paging' % response.meta['max_ts'])
        raise StopIteration

    @property
    def extension(self):
        return self._extension

    @property
    def limit(self):
        return self.limits[self.extension]

    @property
    def root_model(self):
        return self.root_models[self.extension]
