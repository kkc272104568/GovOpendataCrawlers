# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy import FormRequest, Request
from ..items import NanjingopendataItem
from ..utils.LastCrawl import LastCrawl
from ..utils.FileSummary import FilesSummary
from ..utils import toolkit, unify_url


class MasterSpider(scrapy.Spider):
    name = 'master'
    url = 'http://data.nanjing.gov.cn/dataSearch/szf/condition?callback=jQuery'
    last_crawl_time = 0

    def start_requests(self):
        self.last_crawl_time = LastCrawl.crawl_time()
        data = {
            'page': '1',
            'size': '5',
            'type': '',
            'chnlId': '76146'
        }
        yield FormRequest(url=self.url, formdata=data, callback=self.dataset_list_parse)

    def dataset_list_parse(self, response):
        dataset_crawled = 0
        res = response.text
        res_data = res[7: -1]
        response_data = json.loads(res_data)
        for data in response_data['data']:
            metadata = dict()
            dataset_update_time = toolkit.date_to_stamp(data['fanBuRiQi'].split(' ')[0])
            if dataset_update_time < self.last_crawl_time:  # 如果发布时间小于上次爬取时间，就跳过
                dataset_crawled += 1
                continue
            metadata['资源名称'] = data['name']
            metadata['摘要'] = data['zaiYao']
            metadata['数据领域'] = data['shuJuLingYu']
            metadata['关键字'] = data['GuanJiAnZi']
            metadata['数据提供方单位'] = data['ShuJuTiGongFang']
            metadata['发布时间'] = data['fanBuRiQi']
            detail_url = data['docPubUrl']
            yield Request(url=detail_url, callback=self.dataset_file_parse, meta={'metadata': metadata})

        if int(response_data['page']) < int(response_data['totalPage']) and dataset_crawled < 5:
            next_data = {
                'page': str(int(response_data['page']) + 1),
                'size': '5',
                'type': '',
                'chnlId': '76146'
            }
            yield FormRequest(url=self.url, formdata=next_data, callback=self.dataset_list_parse)

    def dataset_file_parse(self, response):
        item = NanjingopendataItem()
        annex = response.xpath('//tr[@class="deep"]//a/@href').extract()[0]
        annex_url = unify_url.unify_url(annex, response)
        item['annex_url'] = annex_url
        item['file_name'] = annex.split('./')[-1]
        item['metadata'] = response.meta['metadata']
        yield item
