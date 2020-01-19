# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy


class FileItem(scrapy.Item):
    file_urls = scrapy.Field()
    headers = scrapy.Field()
    title = scrapy.Field()
    file_names = scrapy.Field()
    metadata = scrapy.Field()
