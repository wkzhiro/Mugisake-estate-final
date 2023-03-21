# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import pymongo

class CheckItemPipeline:
    def process_item(self, item, spider):
        # if not item.get('price'):
        #     raise DropItem('Missing price')        
        return item

class MongoPipeline:
    collection_name = 'suumo_KA02'
    def open_spider(self, spider):
        self.client = pymongo.MongoClient('mongodb+srv://kazushi:test1991@cluster0.6xm5xsd.mongodb.net/?retryWrites=true&w=majority')
        self.db = self.client['property02DB']

    def close_spider(self, item, spider):
        self.client.close()
    
    def process_item(self, item, spider):
        self.db[self.collection_name].insert(dict(item))





