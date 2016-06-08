# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FacebookItem(scrapy.Item):
    id = scrapy.Field()
    type = scrapy.Field()
    data = scrapy.Field()
    meta = scrapy.Field()
