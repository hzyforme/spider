# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import logging
import telnetlib
import random
import redis
import json
import os
import threading
import pdb
from scrapy import signals

from .proxy import initIPPOOLS, updateIPPOOLS
from scrapy.utils.response import response_status_message
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import IgnoreRequest
class ProxyMiddleware(RetryMiddleware):
    '''IP代理'''
    def __init__(self, settings, crawler):
        #自己获取的ip
        self.TIMES = 10
        RetryMiddleware.__init__(self, settings)
        self.rconn = settings.get("RCONN", redis.Redis(crawler.settings.get('REDIS_HOST', 'localhsot'), crawler.settings.get('REDIS_PORT', 6379)))
        #initIPPOOLS(self.rconn)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler)

    def process_request(self,request,spider):
        #pdb.set_trace()
        ipNum=len(self.rconn.keys('IP*'))
        #pdb.set_trace()
        if ipNum<5:
            proxy_thread = threading.Thread(target= initIPPOOLS,args = (self.rconn,))
            proxy_thread.setDaemon(True)
            proxy_thread.start()
            #initIPPOOLS(self.rconn)
        if self.TIMES == 3:
            baseIP=random.choice(self.rconn.keys('IP:*'))
            ip=str(baseIP,'utf-8').replace('IP:','')
            try:
                IP,PORT,status=ip.split(':')
                request.meta['status'] = status
                telnetlib.Telnet(IP,port=PORT,timeout=2) #测试ip是否有效
            except:
                logger.warning("The ip is not available !( IP:%s )" % ip)
                updateIPPOOLS(self.rconn,IP+':'+PORT,status)
            else:
                #pdb.set_trace()
                self.IP = "http://" + IP + ':' + PORT
                logger.warning("The current IP is %s!" % self.IP)
                self.TIMES = 0
                updateIPPOOLS(self.rconn,IP+':'+PORT,status,1)
                #pdb.set_trace()
        else:
            self.TIMES += 1
        #pdb.set_trace()
        if self.IP is not "":
            request.meta["proxy"] = self.IP

    def process_response(self,request,response,spider):
        if response.status in [400,403,404,429,500,502,503,504]:
            self.TIMES = 3
            logger.error("%s! error..." % response.status)
            #pdb.set_trace()
            try:
                updateIPPOOLS(self.rconn,request.meta['proxy'].replace('http://',''),request.meta['status'],-1)
            except:
                pass
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response  # 重试
        else:
            return response

    def process_exception(self, request, exception, spider):
        #pdb.set_trace()
        self.TIMES = 3
        try:
            updateIPPOOLS(self.rconn,request.meta['proxy'].replace('http://',''),request.meta['status'],-1)
        except:
            pass
        return request

class TaobaoSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
