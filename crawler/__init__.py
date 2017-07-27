# coding=utf-8
import requests
import distutils.util
from functools import partialmethod

from config.env import Environment

crawler_env = Environment('CRAWLER')
BASE_PATH = '%s/v4/activities' % crawler_env['HOST']

if not distutils.util.strtobool(Environment('CRAWLER')['VERIFYSSL']):
    old_request = requests.Session.request
    requests.Session.request = partialmethod(old_request, verify=False)
    requests.packages.urllib3.disable_warnings()