#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Spiders a"""

import json
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
from warnings import warn

import dateutil.parser
import requests
from scrapy.http import Response

from common.db import get_session
from common.db.models.activities import Source
from common.utils.progress import ProgressCallbackBase
from .. import BASE_PATH, TSince, headers


def parse_json(response: Response) -> Dict[str, Any]:
    """
    Helper to load the JSON response
    :param response: response to load from
    :return: parsed JSON
    """
    json_body: Dict[str, Any] = json.loads(response.text)
    assert isinstance(json_body, dict), "response must be a json dict"
    return json_body


class ProgressMixin(object):
    # pylint: disable=too-few-public-methods
    """Mixin with a helper message to send status updates to a `ProgressCallbackBase` Progress """

    def __init__(self, progress: Optional[ProgressCallbackBase] = None) -> None:
        self._progress = progress

    def send_progress(self, **kwargs: Any) -> None:
        """
        :param kwargs: meta data to send, can be an arbitrary json serializable
        """
        if self._progress:
            self._progress(**kwargs)


class GenericMixin(object):
    """Common functionality across spiders"""

    def __init__(self,
                 source_id: int,
                 since: Optional[TSince] = None,
                 api_key: Optional[str] = None) -> None:
        """
        :param source_id: source id for this spider
        :param since: since parameter for this spider
        :param api_key: api key for this spider. will be deprecated
        """
        assert source_id is not None
        self._api_key = api_key
        if self._api_key is None:
            with get_session() as session:
                source = session.query(Source).get(source_id)
                self._source = dict(id=source.id,
                                    type=source.type,
                                    uri=source.uri,
                                    slug=source.slug)
        else:
            request_headers = headers(self._api_key)
            self._source = requests.get('%s/sources/%s' % (BASE_PATH, source_id), headers=request_headers).json()
        assert self._source
        if isinstance(since, datetime):
            self._since = since
        elif isinstance(since, str):
            self._since = dateutil.parser.parse(since)
        elif isinstance(since, int) or since is None:
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
        else:
            raise ValueError('Provided since parameter not acceptable')

    @property
    def source(self) -> Dict[str, Any]:
        """:return: the `Source` object of the spider"""
        return self._source

    @property
    def since(self) -> datetime:
        """:return: the since `datetime` of the spider"""
        return self._since

    @property
    def api_key(self) -> Optional[str]:
        """:return: the api key of the spider. will be deprecated"""
        warn("REST Pipeline will be removed in the future", PendingDeprecationWarning)
        return self._api_key
