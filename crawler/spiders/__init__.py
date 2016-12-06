#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
from datetime import datetime, timedelta
from crawler import BASE_PATH


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
    def __init__(self, source_id, since, token):
        assert source_id is not None
        assert token is not None
        self._token = token
        headers = {'Authorization-Token': self.token, 'Content-Type': 'application/json'}
        self._source = requests.get('%s/sources/%s' % (BASE_PATH, source_id), headers=headers).json()
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
    def token(self):
        return self._token

    @property
    def user(self):
        return self._user
