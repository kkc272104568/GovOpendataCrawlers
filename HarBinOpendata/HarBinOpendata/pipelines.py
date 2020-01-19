# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


import json
import os

import shutil
import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.pipelines.files import FilesPipeline

from HarBinOpendata.utlis import toolkit
from HarBinOpendata.utlis.FileSummary import FilesSummary
from HarBinOpendata.utlis.LastCrawl import LastCrawl

cookie = {
    'JSESSIONID': '383D4167D35EB7EDE7D8347944F7C602',
    'sub_domain_cokie': '4%2BhA%2Bz1jscMldTNOYA3f5g%3D%3D',
    'region_name': '%E5%93%88%E5%B0%94%E6%BB%A8',
    'Hm_lvt_c02117f198e6c52d21f611d759eca80c': '579167045,1579242300,1579242350,1579313714',
    'login_type': 'userpwd',
    'sso_token': 'UZjT6wfaFYSiipVsgX5Otg%3D%3D',
    'uc_uid': '5wCFfe%3DWz',
    'login_time': '1579166700',
    'uc_user_id': 'kkc272104568',
    'uc_nick_name': 'babala',
    'Hm_lpvt_c02117f198e6c52d21f611d759eca80c': '1579328436'
}


class HarbinopendataPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        """重写请求生成函数"""
        # dir_name = 'files'
        # if item['metadata']['数据目录名称'] in os.listdir(dir_name):
        #     file_name = 'files/%s' % item['metadata']['数据目录名称']
        #     shutil.rmtree(file_name)
        
        for file_index, file_url in enumerate(item['file_urls']):
            yield scrapy.Request(file_url, cookies=cookie, meta={
                'dataset_name': item['metadata']['数据目录名称'],
                'file_name': item['formdata'][file_index],
                'file_type': item['formate'][file_index],
            }
                                 )
    
    def file_path(self, request, response=None, info=None):
        """重写保存路径函数"""
        return '%s/%s.%s' % (request.meta['dataset_name'], request.meta['file_name'], request.meta['file_type'])
    
    def item_completed(self, results, item, info):
        """重写下载完成钩子函数"""
        dir_name = 'files/%s' % item['metadata']['数据目录名称']
        metadata_json_file = '%s/metadata.json' % dir_name
        try:
            with open(metadata_json_file, 'w', encoding='utf8') as f:
                json.dump(item['metadata'], f, ensure_ascii=False)
        except FileNotFoundError:
            os.mkdir(dir_name)
            with open(metadata_json_file, 'w', encoding='utf8') as f:
                json.dump(item['metadata'], f, ensure_ascii=False)
        
        for i in os.listdir(dir_name):
            if i[-3:] == 'zip':
                filename = 'files/%s/%s' % (item['metadata']['数据目录名称'], i)
                toolkit.un_zip(file_name=filename, dir_name=dir_name)
                os.remove(filename)
                # return item
    
    def close_spider(self, spider):
        dataset_count = FilesSummary.dataset_count()
        size_mb = FilesSummary.size_mb()
        
        settings = get_project_settings()
        data = {
            'address': '172.16.119.3',
            'project_name': settings.get('BOT_NAME'),
            'file_number': dataset_count - LastCrawl.dataset_count(),
            'file_size': size_mb - LastCrawl.total_file_size_mb(),
        }
        print(data)
        LastCrawl.write(dataset_count=dataset_count, total_file_size_mb=size_mb)