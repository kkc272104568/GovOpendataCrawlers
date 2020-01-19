# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import logging
import os

import requests
from scrapy.pipelines.files import FilesPipeline
from scrapy import FormRequest, Request
from scrapy.conf import settings
from ShangHaiOpendata.utils import toolkit
from ShangHaiOpendata.utils.FileSummary import FilesSummary
from ShangHaiOpendata.utils.LastCrawl import LastCrawl


class DatasetDownloadPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        """重写请求生成函数"""
        for file_url in item['file_urls']:
            yield Request(file_url,
                          headers=item['metadata']['headers'],
                          cookies=item['metadata']['cookies'],
                          meta={
                              "dataset_name": item['metadata']['名称']
                                }
                          )

    def file_path(self, request, response=None, info=None):
        """重写保存路径函数"""
        return request.meta['dataset_name']

    def item_completed(self, results, item, info):
        """重写下载完成钩子函数"""
        pass
        # dir_name = 'files/%s' % item['metadata']['名称']
        # zip_file = '%s/file.zip' % dir_name
        # # 解压文件并删除安装包
        # toolkit.un_zip(file_name=zip_file, dir_name=dir_name)
        # os.remove(zip_file)
        # return item

    def close_spider(self, spider):
        dataset_count = FilesSummary.dataset_count()
        size_mb = FilesSummary.size_mb()
        LastCrawl.write(dataset_count=dataset_count, total_file_size_mb=size_mb)
