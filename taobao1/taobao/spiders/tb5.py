# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from taobao.items import TaobaoItem
import urllib
import re
import pdb
import time

class TbSpider(scrapy.Spider):
    name = "tb5"
    allowed_domains = ["taobao.com"]
    start_urls = (
        'https://www.taobao.com/markets/bao/xiangbao?spm=a21bo.2017.201867-main.5.732aee611vzxIE',
    )

    def parse(self, response):
        url=['https://tce.taobao.com/api/mget.htm?callback=jsonp1342&tce_sid=666287,1933212,1953910&tce_vid=1,0,0&tid=,,&tab=,,&topic=,,&count=,,&env=online,online,online','https://tce.taobao.com/api/mget.htm?callback=jsonp888&tce_sid=1932729,1953461&tce_vid=0,0&tid=,&tab=,&topic=,&count=,&env=online,online','https://tce.taobao.com/api/mget.htm?callback=jsonp722&tce_sid=1930530,1932014&tce_vid=0,0&tid=,&tab=,&topic=,&count=,&env=online,online']
        for x in url:
            yield Request(url=x,callback=self.page)
    def page(self,response):
        
        body=response.body.decode("utf-8","ignore")   #获取html源码里的body部分，并设置编码格式为utf-8
        patid='"auction_id":"(.*?)"'                         #正则表达式，用来匹配商品的id
        allid=re.compile(patid).findall(body)         #用python里的re模块来使用正则表达式
        print(allid)
        
        for j in range(0,len(allid)):
            if allid[j]=='0':
                pass
            else:
                thisid=allid[j]
                url1="https://item.taobao.com/item.htm?id="+str(thisid)  #构造商品信息界面的url
                yield Request(url=url1,callback=self.next)

    def next(self,response):
        item=TaobaoItem()
        #pdb.set_trace()
        item['key'] = '箱包'
        try:
            item["title"]=response.xpath("//h3[@class='tb-main-title']/@data-title").extract()[0] #提取title
            intro = response.xpath('//ul[@class="attributes-list"]//li/text()').extract()
            intro = str(intro).replace('\\xa0','')
            intro = eval(intro)
            item['intro'] = intro
            item["link"]=response.url                                                         #提取当前页面的url
            patid='id=(.*?)$'                              
            thisid=re.compile(patid).findall(response.url)[0]     #用正则表达式通过url来提取商品的id
            clickurl = 'https://count.taobao.com/counter3?callback=jsonp86&keys=ICCP_1_' + str(thisid)
            clickdata = urllib.request.urlopen(clickurl).read().decode("utf-8","ignore")
            click = re.findall(':(\d+)',clickdata)
            item['click'] = click[0]
            commenturl="https://rate.taobao.com/detailCount.do?callback=jsonp100&itemId="+str(thisid) #构造抓包获得的url（评论数）
            #print(commenturl)
            commentdata=urllib.request.urlopen(commenturl).read().decode("utf-8","ignore")  #进入构造出的url，并读取页面源码信息
            #print(commentdata)
            pat='"count":(.*?)}'
            item["comment"]=re.compile(pat).findall(commentdata)[0]    #用正则表达式来匹配提取出商品评价的数量
            referer = response.url
            headers = {'Referer':referer}
            seldurl = 'https://detailskip.taobao.com/service/getData/1/p1/item/detail/sib.htm?itemId='+str(thisid)+'&modules=soldQuantity,xmpPromotion&callback=onSibRequestSuccess'
            request = urllib.request.Request(seldurl,headers=headers)
            runtime = 1
            while True:
                if runtime > 5:
                    break
                try:
                    selddata = urllib.request.urlopen(request).read().decode("utf-8","ignore")
                    selddata = selddata.replace('\r','').replace('\n','').replace('onSibRequestSuccess(','').replace(');','').replace('true','1').replace('false','0')
                    seld_dict = eval(selddata)
                    seld = seld_dict['data']['soldQuantity']['confirmGoodsCount']
                    item['seld'] = seld
                    break
                except:
                    time.sleep(1)
                    runtime += 1
            try:
                price = seld_dict['data']['promotion']['promoData']['def'][0]['price']
                item["price"] = price
            except:
                item["price"]=response.xpath("//em[@class='tb-rmb-num']/text()").extract()[0]       #提取原价
            item['extract_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            description = response.xpath('//p[@class="tb-subtitle"]/text()').extract()
            if description:
                item['description'] = description[0]
            else:
                description = response.xpath('//p[@class="newp"]/text()').extract()
                if description:
                    item['description'] = description[0]
            #pdb.set_trace()
            #print(item["comment"])
            yield item
            
        except:
            pass
        
