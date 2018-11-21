# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TiebanameItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tid=scrapy.Field()
    name=scrapy.Field()
    tiename=scrapy.Field()
    _id=scrapy.Field()
