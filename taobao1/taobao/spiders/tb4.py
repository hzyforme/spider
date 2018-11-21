# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from taobao.items import TaobaoItem
import urllib
import re
import pdb
import time
class TbSpider(scrapy.Spider):
    name = "tb4"
    redis_key="taobao1:start_urls"
    allowed_domains = ['taobao.com']
    header={
        'Host':'list.taobao.com',
        'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding':'gzip, deflate, br',
        'Cookie':'t=757dc685435bd5f4e1f22922df0b77b6; cna=7FoxEnzHOEwCAduZPmEj1yIt; isg=AmNjVg-xPqKwdvLRZGZ9rPFm864HWPWVtKi_K5XAYkI51IP2HSiH6kFOuJ6l; um=65F7F3A2F63DF0202D360E52AD3259A25C36917A6545C6D3F578573A530DD491E76019A7B7A72823CD43AD3E795C914C8F844405CF5C9BE9CF4F1ADE6EC96EE8; miid=2010897650437729537; thw=cn; l=AqOjkngplv9znhaqhHU29pdnM-xN4jfa; cookie2=1e9a21f8af642fca4d4e14279141c0c6; v=0; _tb_token_=546beba7ea1e; hng=CN%7Czh-CN%7CCNY%7C156; mt=ci%3D-1_0; linezing_session=KEpcuu3G64EEBvQB4F4uqXZy_1508411430533hV7l_2',
        'Connection':'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control':'max-age=0',
        }
    def start_requests(self):
        url='https://www.taobao.com/market/nvbao/citiao/djb.php?spm=a217q.8031046.323457-static.2.2f3d92ae86sI5I'
        yield Request(url=url,callback=self.parse,headers=self.header,dont_filter=True)
    def parse(self, response):
        time.sleep(3)
        for x in range(0,99):
            
            url='https://list.taobao.com/itemlist/mini/list.htm?pSize=60&json=on&_input_charset=utf-8&spm=a2106.2206569.0.0.Ib9HUh&cat=50072721&sort=biz30day&user_type=0&at=12034&as=1&viewIndex=1&atype=b&s=0&style=grid&same_info=1&tid=0&isnew=2&filter=reserve_price[20,100000000]&data-key=s&data-value='+str(x*60)+'&data-action&module=page&_ksTS=1508417013502_626&callback=jsonp627'
            yield Request(url=url,callback=self.page,headers=self.header,dont_filter=True)


    def page(self,response):
        
        body=response.body.decode("utf-8","ignore")   #获取html源码里的body部分，并设置编码格式为utf-8
        patid='"itemId":"(.*?)"'                         #正则表达式，用来匹配商品的id
        allid=re.compile(patid).findall(body)     #用python里的re模块来使用正则表达式
        print(allid)
        for j in range(0,len(allid)):
            thisid=allid[j]
            url1="https://item.taobao.com/item.htm?id="+str(thisid)  #构造商品信息界面的url
            yield Request(url=url1,callback=self.next,headers=self.header,dont_filter=True)

    def next(self,response):
        item=TaobaoItem()
        #pdb.set_trace()
        item['key'] = '单肩包女'
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