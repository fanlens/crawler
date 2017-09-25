# coding=utf-8
from functools import partialmethod

import requests

from config import get_config

_config = get_config()
BASE_PATH = '%s/%s/activities' % (_config.get('DEFAULT', 'version'), _config.get('CRAWLER', 'api_host'))


def api_path(*parts):
    return BASE_PATH + '/' + '/'.join(map(str, parts))


def headers(api_key):
    return {'Authorization': api_key, 'Content-Type': 'application/json'}


if not _config.getboolean('CRAWLER', 'verifyssl', fallback=False):
    old_request = requests.Session.request
    requests.Session.request = partialmethod(old_request, verify=False)
    requests.packages.urllib3.disable_warnings()
