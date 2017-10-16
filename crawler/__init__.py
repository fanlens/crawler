
"""The main crawling module."""
from datetime import datetime
from functools import partialmethod
from typing import Dict, Union

import requests

from common.config import get_config

TSince = Union[str, int, datetime]

_CONFIG = get_config()
BASE_PATH = '%s/%s/activities' % (_CONFIG.get('DEFAULT', 'version'), _CONFIG.get('CRAWLER', 'api_host'))


def api_path(*parts: str) -> str:
    """
    Build a url path str for the fanlens api
    :param parts: path elements
    :return: a url pointing to the fanlens api
    """
    return BASE_PATH + '/' + '/'.join(map(str, parts))


def headers(jwt_token: str) -> Dict[str, str]:
    """
    Required headers to interact with the fanlens api
    :param jwt_token: jwt_token
    :return: a dictionary of headers
    """
    return {'Authorization': jwt_token, 'Content-Type': 'application/json'}


if not _CONFIG.getboolean('CRAWLER', 'verifyssl', fallback=True):
    # sys.modules mangling pylint: disable=no-member
    _OLD_REQUEST = requests.Session.request
    requests.Session.request = partialmethod(_OLD_REQUEST, verify=False)  # type: ignore
    requests.packages.urllib3.disable_warnings()  # type: ignore
