#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from utils import now
from db.models.facebook import get_since, FacebookPostEntry, FacebookCommentEntry, FacebookReactionEntry


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


class FacebookMixin(object):
    allowed_domains = ["facebook.com"]
    root_models = {
        'post': FacebookPostEntry,
        'comments': FacebookCommentEntry,
        'reactions': FacebookReactionEntry
    }
    limits = {
        'post': 50,
        'comments': 700,
        'reactions': 4000
    }

    def __init__(self, page, since, root_model):
        assert len(page) > 0
        if since is None:
            since = -14  # default -14 days
        if since == 'cont':
            self.logger.info('fetching last post timestamp')
            # todo irrelevant for extensions crawler?
            self._since = get_since(root_model, page)
        else:
            try:
                since_int = int(since)
                if since_int < 0:
                    self._since = now(millis=False) + since_int * 86400
                else:
                    self._since = since
            except ValueError:
                self._since = since
        self._page = page

    @property
    def page(self):
        return self._page

    @property
    def since(self):
        return self._since
