# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    key = scrapy.Field()
    title=scrapy.Field()
    link=scrapy.Field()
    price=scrapy.Field()
    comment=scrapy.Field()
    intro = scrapy.Field()
    click = scrapy.Field()
    seld = scrapy.Field()
    description = scrapy.Field()
    extract_time = scrapy.Field()