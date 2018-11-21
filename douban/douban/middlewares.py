# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import pickle
from scrapy import signals


class DoubanSpiderMiddleware(object):
    pass

class CookieMiddleware(object):
    cookie=pickle.load(open('/home/softcloud/douban/douban/cookies.ini','rb'))
    def process_request(self,request,spider):
        request.cookies=self.cookie

