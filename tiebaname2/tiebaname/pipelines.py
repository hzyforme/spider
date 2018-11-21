# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os.path
import json
import codecs
import redis
from tiebaname.items import TiebanameItem
import pymongo
class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('cnblogs.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()

class TiebanamePipeline(object):
    def process_item(self, item, spider):
        name=item['name'].encode('utf8')
        tiename=item['tiename'].encode('utf8')
        url=item['url'].encode('utf8')
        nameid=item['nameid'].encode('utf8')
        conn=MySQLdb.connect(
            host = '127.0.0.1',
            db = 'scrapyDB',
            user = 'root',
            passwd = '111111',
            port = 3306,
            charset='utf8')
        cur=conn.cursor()
        cur.execute("INSERT INTO tiebaname(nameid,name,tiename,url) values(%s,%s,%s)",(nameid,name,tiename,url))
        cur.close()
        conn.commit()
        conn.close()
        return item


class Tiebaname2Pipline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls,crawler):
        return cls(
                mongo_uri = crawler.settings.get('MONGO_URI'),
                mongo_db = crawler.settings.get('MONGO_DATABASE','tieba')
            )

    def open_spider(self,spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self,spider):
        self.client.close()

    def process_item(self, item, spider):
        if isinstance(item, TiebanameItem):
            self._process_user_item(item)
        else:
            print ('sdsa')
        return item
    def _process_user_item(self,item):
        self.db.tieb.insert(dict(item))
