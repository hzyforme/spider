# -*- coding: utf-8 -*-
import scrapy
import scrapy
from tiebaname.items import TiebanameItem
from scrapy.http import Request
import pdb
import re
import codecs
from tiebaname.scrapy_redis.spiders import RedisSpider

class BaidutiebaSpider(RedisSpider):
    name = 'baidutieba'
    redis_key="baidutieba:start_urls"
    allowed_domains = ['baidu.com']
    start_urls = ['http://tieba.baidu.com/f/index/forumclass']
    #header = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36 SE 2.X MetaSr 1.0"}
    def start_requests(self):
        start_urls = 'http://tieba.baidu.com/f/index/forumclass'
        yield Request(url=start_urls,callback=self.parse,dont_filter=True)
    def parse(self, response):
        
        href=response.xpath('//ul[@class="item-list-ul clearfix"]/li/a/@href').extract()
        for x in href:
        	url="http://tieba.baidu.com"+str(x)
        	
        	yield Request(url=url,callback=self.page,dont_filter=True)
    def page(self,response):
    	url=response.url
    	pageurl=response.xpath('//a[@class="last"]/@href').extract()
    	if pageurl:
    		pageurl=pageurl[0]
    		hh='pn=[1-9]\d*'
    		k=re.compile(hh).findall(pageurl)
    		k=k[0]
    		cc='[1-9]\d*'
    		ID=re.compile(cc).findall(k)
    		times=ID[0]
    		times=int(times)
    		current_url=response.url
    		for x in range(1,times):
    			url=current_url+'&st=new&'+'pn='+str(x)
    			yield Request(url=url,callback=self.next,dont_filter=True)
    	else:
    		yield Request(url=url,callback=self.next,dont_filter=True)
    def next(self,response):
    	href=response.xpath('//div[@class="ba_info"]/a/@href').extract()
    	if href:
    		for x in href:
    			url="http://tieba.baidu.com"+str(x)
    			yield Request(url=url,callback=self.next2,dont_filter=True)
    	else:
    		print('none')
    def next2(self,response):
        page=response.xpath('//a[@class="last pagination-item "]/@href').extract()
        url=response.url
        if page:
            page=page[0]
            hh='pn=[1-9]\d*'
            k=re.compile(hh).findall(page)
            k=k[0]
            cc='[1-9]\d*'
            ID=re.compile(cc).findall(k)
            times=ID[0]
            times=int(int(times)/50)
            current_url=response.url
            for x in range(0,times):
                url=current_url+'&ie=utf-8&pn='+str(50*x)
                yield Request(url=url,callback=self.next3,dont_filter=True)
        else:
            yield Request(url=url,callback=self.next3,dont_filter=True)
    def next3(self,response):
        kk=response.text
        hh='href="/p/[1-9]\d*"'
        href=re.compile(hh).findall(kk)
        if href:
            for x in href:
                cc='/p/[1-9]\d*'
                dd=href[0]
                ff=re.compile(cc).findall(dd)
                url="http://tieba.baidu.com"+str(ff[0])
                yield Request(url=url,callback=self.next4)
        else:
            print('none2')
    def next4(self,response):
        item=TiebanameItem()
        url=response.url
        cc='[1-9]\d*'
        item['tid']=re.compile(cc).findall(url)[0]
        tiename=response.xpath('//div[@class="core_title_wrap core_title_wrap_bright"]/div/h1/text()').extract()
        other=response.xpath('//div[@class="left_section"]/div/h3/text()').extract()
        another=response.xpath('//div[@class="left_section"]/div/h3/@title').extract()
        if tiename:
            item['tiename']=tiename[0]
        else:
            if other:
                item['tiename']=other[0]
            else:
                if another:
                    item['tiename']=another[0]

        ID=response.xpath('//li[@class="d_name"]/@data-field').extract()
        if ID:
            data=ID[0]
            nameid=re.compile('[1-9]\d*').findall(data)[0]
            item['_id']=nameid
        name=response.xpath('//li[@class="d_name"]/a/text()').extract()
        if name:
            item['name']=name[0]
        yield item
