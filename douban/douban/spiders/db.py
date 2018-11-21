# -*- coding: utf-8 -*-
import scrapy
import pdb
import re
import json
from scrapy.http import Request
from ..items import DoubanItem,Short_commentItem,Long_moviecommentItem,DisscussItem
class DbSpider(scrapy.Spider):
    name = "db"
    #allowed_domains = ["movie.douban.com"]
    url3='https://movie.douban.com/j/review/{num}/full'
    start_urls = ['https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=%E5%BE%AE%E7%94%B5%E5%BD%B1&start=0','https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=短片&start=0']
    url='https://movie.douban.com/j/new_search_subjects?sort=T&range=0,10&tags=%E5%BE%AE%E7%94%B5%E5%BD%B1&start={num}'
    url1='https://movie.douban.com/subject/{id}/comments?start={num}&limit=20&sort=new_score&status=P&percent_type='
    url2='https://movie.douban.com/subject/{id}/reviews?start={num}'
    url4='https://movie.douban.com/subject/{id}/discussion/?start={num}&sort_by=time'

    def parse(self, response):
        Item=DoubanItem()
        doc=json.loads(response.text)
        #pdb.set_trace()
        for i in range(0,20):
            url=doc['data'][i]['url']
            Item['rate']=doc['data'][i]['rate']
            Item['star']=doc['data'][i]['star']
            yield Request(url=url,callback=self.next,meta={'item':Item})
        if doc['data']!='':
            try:
                num=response.meta['num']+20
            except:
                num=20
            yield Request(url=self.url.format(num=num),callback=self.parse,meta={'num':num})
            
    def next(self,response):
        Item=response.meta['item']
        #pdb.set_trace()
        Item['_id']=re.compile(r'https://movie.douban.com/subject/(\d+?)/').findall(response.url)[0]
        Item['url']=response.url
        Item['Movie_title']=response.xpath('/html/body/div[3]/div[1]/h1/span[1]/text()').extract()[0]
        Item['comment_num']=response.xpath('//div[@class="rating_sum"]/a/span/text()').extract()[0] or ''
        #pdb.set_trace()
        percentage=response.xpath('//div[@class="ratings-on-weight"]/div')
        percen={}
        #pdb.set_trace()
        for i in percentage:
            a=i.xpath('span/text()').extract()
            percen[a[0].strip()]=a[1]
            percen.update(percen)
        Item['star_percentage']=percen
        Item['director']=response.xpath('/html/body/div[3]/div[1]/div[2]/div[1]/div[1]/div[1]/div[1]/div[2]/span[1]/span[2]/a/text()').extract()[0] or ''
        try:
            Item['Movie_type']=response.xpath('//span[@property="v:genre"]/text()').extract()[0]
        except:
            pass
        allinfo=response.xpath('//div[@id="info"]').xpath('string(.)').extract()[0]
        country=re.compile('制片国家/地区: [^\x00-\xff]*').findall(allinfo)[0]
        try:
            pianchang=re.compile('片长: \d分\d+秒').findall(allinfo)[0]
        except:
            pass
        
        try:
            Item['Release_time']=response.xpath('//span[@property="v:initialReleaseDate"]/text()').extract()[0]
        except:
            pass
        try:

            Item['Movie_length']=response.xpath('//span[@property="v:runtime"]/text()').extract()[0]
        except:
            try:
                Item['Movie_length']=pianchang.split()[1]
            except:
                pass
        try:
            Movie_Synopsis=response.xpath('/html/body/div[3]/div[1]/div[2]/div[1]/div[3]/div/span[1]/text()').extract()[0].replace('\u3000\u3000','').replace('\n','')
            try:
                movie2=response.xpath('/html/body/div[3]/div[1]/div[2]/div[1]/div[3]/div/span[1]/text()').extract()[1].replace('\u3000\u3000','').replace('\n','')
                Item['Movie_Synopsis']=Movie_Synopsis+movie2
            except:
                Item['Movie_Synopsis']=Movie_Synopsis
                pass
        except:
            Item['Movie_Synopsis']=response.xpath('//span[@class="all hidden"]').xpath('string(.)').extract()
        try:
            Item['Watched_people']=re.compile('\d+').findall(response.xpath('/html/body/div[3]/div[1]/div[2]/div[2]/div[7]/div/a[1]/text()').extract()[0])[0]
        except:
            pass
        try:
            Item['Want_Watch_people']=re.compile('\d+').findall(response.xpath('/html/body/div[3]/div[1]/div[2]/div[2]/div[7]/div/a[2]/text()').extract()[0])[0]
        except:
            pass
        try:
            Item['long_moviecomment_num']=response.xpath('//*[@id="content"]/div[2]/div[1]/section/header/h2/span/a/text()').extract()[0]
        except:
            pass
        try:
            Item['short_comment_num']=response.xpath('//*[@id="comments-section"]/div[1]/h2/span/a/text()').extract()[0]
        except:
            pass
        yield Item        
        yield Request(url=self.url1.format(num=0,id=Item['_id']),callback=self.after1)
        yield Request(url=self.url2.format(num=0,id=Item['_id']),callback=self.after2)
        yield Request(url=self.url4.format(num=0,id=Item['_id']),callback=self.disscuss)
        #yield Item

    def after1(self,response):        
        #pdb.set_trace()        
        for i in range(0,20): 
            try:
                Item=Short_commentItem()
                Item['Id']=re.compile(r'https://movie.douban.com/subject/(\d+?)/').findall(response.url)[0]
                Item['commentator']=response.xpath('//span[@class="comment-info"]/a/text()').extract()[i]
                Item['short_comment']=response.xpath('//div[@class="comment"]/p/text()').extract()[i].strip()
                Item['short_comment_time']=response.xpath('//span[@class="comment-time "]/@title').extract()[i]
                Item['good']=response.xpath('//span[@class="comment-vote"]/span/text()').extract()[i]
                yield Item
            except:
                pass
        try:      
            if Item['commentator']!='':
                try:
                    num=response.meta['num']+20
                except:
                    num=20
                yield Request(url=self.url1.format(num=num,id=Item['Id']),callback=self.after1,meta={'num':num})
        except:
            pass

    def after2(self,response):
        a='//*[@id="content"]/div/div[1]/div[1]/div[{num}]//@data-cid'
        cid=re.compile(r'https://movie.douban.com/subject/(\d+?)/').findall(response.url)[0]
        for i in range(0,20):
            Item=Long_moviecommentItem()
            Item['cid']=re.compile(r'https://movie.douban.com/subject/(\d+?)/').findall(response.url)[0]
            Id=response.xpath(a.format(num=i+1)).extract()[0]
            Item['commentator']=response.xpath('//a[@class="name"]/text()').extract()[i]
            Item['respon']=response.xpath('//*[@id='+str(Id)+']/div/div[3]/a[3]/text()').extract()[i]
            Item['bad']=response.xpath('//span[@id="r-useful_count-'+str(Id)+'\"]/text()').extract()[i].strip()
            Item['good']=response.xpath('//span[@id="r-useless_count-'+str(Id)+'\"]/text()').extract()[i].strip()
            Item['long_moviecomment_time']=response.xpath('//span[@class="main-meta"]/text()').extract()[i]
            yield Request(url=self.url3.format(num=Id),callback=self.after21,meta={'item':Item})
        try:
            if Item['commentator']!='':
                try:
                    num=response.meta['num']+20
                except:
                    num=20
                yield Request(url=self.url2.format(num=num,id=cid),callback=self.after2,meta={'num':num})
        except:
            pass

    def after21(self,response): 
        Item=response.meta['item']
        #re.compile(r'<br>(.+?)<br>').findall(response.text).replace('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;','')
        #pdb.set_trace()
        long_moviecomment= re.compile(r'"html":"(.+?)"').findall(response.text)[0].replace('<br>','').replace('<\/p>','').replace('<p>','').replace(' ','')
        Item['long_moviecomment']=long_moviecomment.replace('&nbsp;','')
        yield Item

    def disscuss(self,response):
        Item=DisscussItem()
        #pdb.set_trace()
        topic=response.xpath('//table[@id="posts-table"]/tr/td/a/@title').extract()
        for i in range(0,len(topic)):
            k=i+2
            Item['uid']=re.compile(r'https://movie.douban.com/subject/(\d+?)/').findall(response.url)[0]
            Item['topic']=response.xpath('//table[@id="posts-table"]/tr/td/a/@title').extract()[i]
            Item['commentator']=response.xpath('//table[@id="posts-table"]/tr/td[2]/a/text()').extract()[i].strip()
            Item['respon']=response.xpath('//table[@id="posts-table"]/tr/td[3]/text()').extract()[i+1]
            Item['update_time']=response.xpath('//table[@id="posts-table"]/tr/td[4]/text()').extract()[i+1]
            yield Item
        try:
            if Item['topic']!='':
                #pdb.set_trace()
                try:
                    num=response.meta['num']+20
                except:
                    num=20
                yield Request(url=self.url4.format(num=num,id=Item['uid']),callback=self.disscuss,meta={'num':num})
        except:
            pass
