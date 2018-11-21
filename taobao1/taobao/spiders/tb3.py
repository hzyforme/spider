# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from taobao.items import TaobaoItem
import urllib
import re
import pdb
import time

class TbSpider(scrapy.Spider):
    name = "tb3"
    allowed_domains = ["taobao.com"]
    start_urls = (
        'http://www.taobao.com/',
    )
    key_list = [
                    "手机",
                    "耳机入耳式",
                    "耳机头戴式",
                    '耳机 挂耳式',
                    '耳机 耳塞式',
                    '耳机蓝牙',
                    '相机单反机 高清 数码',
                    '笔记本电脑',
                    '笔记本电脑 游戏本',
                    '笔记本电脑 联想',
                    '商务笔记本电脑',
                    '平板电脑',
                    'diy电脑主机',
                    '电饭煲 智能',
                    '电饭煲 智能小',
                    '电饭煲 家用',
                    '电磁炉 家用',
                    '电磁炉锅',
                    '电磁炉特价 家用 智能',
                    '液晶电视',
                    '液晶电视机32寸特价',
                    '液晶电视55寸',
                    '液晶电视机',
                    '平板电视机',
                    '平板电视机 智能',
                    '微波炉 家用',
                    '微波炉 家用 智能',
                    '智能手环',
                    '智能手环男',
                    '智能手环 心率 血压',
                    '智能手环蓝牙耳机',
                    '智能手表男',
                    '智能手表 多功能',
                    '智能手表 多功能 学生',
                    '冰箱双开门',
                    '冰箱双门 家用',
                    '冰箱三门',
                    '冰箱小型',
                    '电水壶 家用',
                    '电水壶 烧水壶大容量',
                    '电吹风家用',
                    '电吹风大功率 理发店',
                    '电吹风家用 不伤发',
                    '电动牙刷 成人',
                    '电动牙刷 儿童',
                    '电动剃须刀男 充电式',
                    '电动剃须刀 飞利浦',
                    '电动剃须刀 飞科',
                ]

    def parse(self, response):
        for i in range(36,48):
            key = self.key_list[i]
            #key=self.key_list[0]                  #搜索关键字：零食
            for i in range(0,101):
                url="https://s.taobao.com/search?q="+str(key)+"&s="+str(44*i)   #构造页码的url
                yield Request(url=url,callback=self.page,meta={'key':key})
    def page(self,response):
        body=response.body.decode("utf-8","ignore")   #获取html源码里的body部分，并设置编码格式为utf-8
        patid='"nid":"(.*?)"'                         #正则表达式，用来匹配商品的id
        allid=re.compile(patid).findall(body)         #用python里的re模块来使用正则表达式
        print(allid)
        for j in range(0,len(allid)):
            thisid=allid[j]
            url1="https://item.taobao.com/item.htm?id="+str(thisid)  #构造商品信息界面的url
            yield Request(url=url1,callback=self.next,meta={'key':response.meta['key']})

    def next(self,response):
        item=TaobaoItem()
        #pdb.set_trace()
        item['key'] = response.meta['key']
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