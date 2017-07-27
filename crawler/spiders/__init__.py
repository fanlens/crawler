#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timedelta
from crawler import BASE_PATH
from db import DB
from db.models.activities import Source


def parse_json(fun):
    def wrapped(self, response, *args, **kwargs):
        kwargs['json_body'] = json.loads(response.body_as_unicode())
        yield from fun(self, response, *args, **kwargs)

    return wrapped


class ProgressMixin(object):
    def __init__(self, progress=None):
        self._progress = progress

    def send_progress(self, **kwargs):
        if self._progress is not None:
            self._progress(**kwargs)


class GenericMixin(object):
    def __init__(self, source_id, since, api_key):
        assert source_id is not None
        self._api_key = api_key
        if self._api_key is None:
            with DB().ctx() as session:
                source = session.query(Source).get(source_id)
                self._source = dict(id=source.id,
                                    type=source.type.value,
                                    uri=source.uri,
                                    slug=source.slug)
        else:
            headers = {'Authorization-Token': self.api_key, 'Content-Type': 'application/json'}
            self._source = requests.get('%s/sources/%s' % (BASE_PATH, source_id), headers=headers).json()
        assert self._source
        if since is None:
            since = -14  # default -14 days
        try:
            since_int = int(since)
            if since_int < 0:
                self._since = datetime.utcnow() - timedelta(days=-since_int)
            else:
                self._since = datetime.utcfromtimestamp(since_int)
        except ValueError:
            self._since = datetime.utcnow()

    @property
    def source(self):
        return self._source

    @property
    def since(self):
        return int(self._since.timestamp())

    @property
    def since_dt(self):
        return self._since

    @property
    def api_key(self):
        return self._api_key

    @property
    def user(self):
        return self._user
