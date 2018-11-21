# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id=scrapy.Field()
    url =scrapy.Field()
    Movie_title=scrapy.Field()
    director=scrapy.Field()
    Movie_type=scrapy.Field()
    country=scrapy.Field()
    Release_time=scrapy.Field()
    Movie_length=scrapy.Field()
    rate=scrapy.Field()
    star=scrapy.Field()
    Movie_Synopsis=scrapy.Field()
    Watched_people=scrapy.Field()
    Want_Watch_people=scrapy.Field()
    long_moviecomment_num=scrapy.Field()
    short_comment_num=scrapy.Field()
    comment_num=scrapy.Field()
    star_percentage=scrapy.Field()

class Short_commentItem(scrapy.Item):
    Id=scrapy.Field()
    commentator=scrapy.Field()
    good=scrapy.Field()
    short_comment=scrapy.Field()
    short_comment_time=scrapy.Field()

class Long_moviecommentItem(scrapy.Item):
    cid=scrapy.Field()
    commentator=scrapy.Field()
    good=scrapy.Field()
    bad=scrapy.Field()
    respon=scrapy.Field()
    long_moviecomment=scrapy.Field()
    long_moviecomment_time=scrapy.Field()

class DisscussItem(scrapy.Item):
    uid=scrapy.Field()
    topic=scrapy.Field()
    commentator=scrapy.Field()
    respon=scrapy.Field()
    update_time=scrapy.Field()
