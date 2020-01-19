# -*- coding: utf-8 -*-
import scrapy
import json

from ..items import HenanopendataItem
from ..utlis import toolkit
from ..utlis.LastCrawl import LastCrawl


class HenanSpider(scrapy.Spider):
    name = 'henan'
    sun_number = 0
    add_numbers = 6
    last_crawl_time = LastCrawl.crawl_time()
    
    url = 'http://data.hnzwfw.gov.cn/odweb/catalog/catalog.do?method=GetCatalog'
    cata_url = 'http://data.hnzwfw.gov.cn/odweb/catalog/catalogDetail.htm?cata_id='
    down_url = 'http://data.hnzwfw.gov.cn/odweb/catalog/catalogDetail.do?method=GetDownLoadInfo'
    file_url = 'http://data.hnzwfw.gov.cn/odweb/catalog/CatalogDetailDownload.do?method=getFileDownloadAddr&fileId=%s'
    
    form_data1 = {
        'start': '0',
        'length': '6',
        'pageLength': '6',
        '_order': 'cc.update_time desc'
    }
    
    form_data2 = {
        'cata_id': '',
        'conf_type': '2',
        'file_type': '1,3',
    }
    
    def start_requests(self):
        yield scrapy.FormRequest(
            url=self.url,
            formdata=self.form_data1,
            callback=self.get_url_list
        )
    
    def get_url_list(self, response):
        dataset_crawled = 0
        data_info = json.loads(response.text)['data']
        # 判断更新事件时间是否大于上次爬取时间，如果大于，爬取数据，不大于，则直接跳出爬虫
        for info in data_info:
            dataset_update_time = info['update_time']
            dataset_update_time = dataset_update_time.split(' ')[0]
            dataset_update_time = toolkit.date_to_stamp(dataset_update_time)
            # print('@@@@@@@@@', dataset_update_time, info['description'])
            if dataset_update_time > self.last_crawl_time:
                new_url = self.cata_url + info['cata_id']
                yield scrapy.Request(
                    url=new_url,
                    callback=self.get_download_info,
                    meta={
                        'cata_id': info['cata_id']
                    }
                )
            else:
                dataset_crawled += 1
        
        # print('step 2step 2step 2step 2step 2step 2step 2step 2step 2')
        if dataset_crawled >= 6:
            # print('yes')
            return
        else:
            self.sun_number += self.add_numbers
            self.form_data1['start'] = str(self.sun_number)
            # print(str(self.sun_number))
            yield scrapy.FormRequest(
                url=self.url,
                formdata=self.form_data1,
                callback=self.get_url_list
            )
    
    def get_download_info(self, response):
        metadata = dict()
        metadata_header = response.xpath('*//div[@class="info-list"]//div[@class="info-header"]//text()').extract()
        metadata_body = response.xpath('*//div[@class="info-list"]//div[@class="info-body"]')
        for index, info in enumerate(metadata_header):
            value = metadata_body[index].xpath('text()').extract_first()
            if value:
                metadata[info] = toolkit.remove_blanks(value)
            else:
                metadata[info] = value
        
        self.form_data2['cata_id'] = response.meta['cata_id']
        
        yield scrapy.FormRequest(
            url=self.down_url,
            formdata=self.form_data2,
            callback=self.get_download_url_list,
            meta={
                'metadata': metadata,
                'cata_id': response.meta['cata_id']
            }
        )
    
    def get_download_url_list(self, response):
        item = HenanopendataItem()
        file_list = json.loads(response.text)
        download_url_list = []
        download_url_list_name = []
        download_url_list_type = []
        for file in file_list['data']:
            download_url_list.append(self.file_url % (file['fileId']))
            download_url_list_name.append(file['fileName'])
            download_url_list_type.append(file['fileFormat'])
        item['file_urls'] = download_url_list
        item['metadata'] = response.meta['metadata']
        item['formdata'] = download_url_list_name
        item['formate'] = download_url_list_type
        yield item
