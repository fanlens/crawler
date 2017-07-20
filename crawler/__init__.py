# coding=utf-8
from config.env import Environment

crawler_env = Environment('CRAWLER')
BASE_PATH = '%s/v4/activities' % crawler_env['HOST']
