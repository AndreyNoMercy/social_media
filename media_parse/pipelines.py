# -*- coding: utf-8 -*-
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from config import DB_hello_moda
from config import DB_bereg_resort
from config import DB_hydroflight

class MediaParsePipeline:
    def process_item(self, item, spider):
        return item

class HelloModaFollowersParsePipeline:
    def process_item(self, item, spider):
        collection = DB_hydroflight[spider.name]
        collection.insert(item)
        return item

