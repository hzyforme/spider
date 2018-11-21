# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from .items import DoubanItem,Short_commentItem,Long_moviecommentItem,DisscussItem

class Douban2Pipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
                mongo_uri = crawler.settings.get('MONGO_URI'),
                mongo_db = crawler.settings.get('MONGO_DATABASE','db')
            )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item,DoubanItem):
            self._process_douban_item(item)
        if isinstance(item, Short_commentItem):
            self._process_short_item(item)
        if isinstance(item, Long_moviecommentItem):
            self._process_long_item(item)
        if isinstance(item,DisscussItem):
            self._process_disscuss_item(item)
        return item

    def _process_douban_item(self,item):
        self.db.doubaninfo.insert(dict(item))
    def _process_short_item(self,item):
    	self.db.short.insert(dict(item))
    def _process_long_item(self,item):
    	self.db.long.insert(dict(item))
    def _process_disscuss_item(self,item):
        self.db.disscuss.insert(dict(item))



    
