# -*- coding: utf-8 -*-
import re
import time

import scrapy
from ..items import FileItem
from ..util.LastCrawl import LastCrawl
from ..util import toolkit
from ..util import parse_err
import json


class JnopenSpider(scrapy.Spider):
    name = 'jnopen'
    page = 0
    last_crawl_time = LastCrawl.crawl_time()
    form_data = {
        'group_id': '',
        'start': '0',
        'length': '10',
        'pageLength': '10',
        'cata_type': '',
        'keywords': '',
        'use_type': '',
        'catalog_format': '',
        'org_code': '',
        '_order': 'cc.datafile_update_time desc'
    }

    def start_requests(self):
        """
        爬虫起点函数，重写父类方法
        :return: None
        """
        url = 'http://data.jinan.gov.cn/odweb/catalog/catalog.do?method=GetCatalog'
        yield scrapy.FormRequest(
            url=url,
            formdata=self.form_data,
            callback=self.only_unstructured_parse,
            dont_filter=False
        )

    def only_unstructured_parse(self, response):
        """
        解析详情页, 采集数据仅有非结构化类型数据
        :param response: 请求详情页后返回的 response
        :return: None
        """
        dataset_crawled = 0
        data_list = json.loads(response.body.decode())['data']

        if len(data_list) == 0:
            # 打印详情页列表未找到错误
            parse_err.log(parse_err.NO_LIST, 'paper_list', '数据集列表', response)
            return
        for data in data_list:
            cata_id = data['cata_id']
            cata_title = data['cata_title']
            update_time = toolkit.date_to_stamp(data['conf_datafile_update_time'])
            # 如果更新时间大于上次爬取的时间 则下载数据集
            if update_time > self.last_crawl_time:
                # 元数据页面请求
                yield scrapy.Request(
                            url='http://data.jinan.gov.cn/odweb/catalog/catalogDetail.htm?cata_id=%s' % cata_id,
                            callback=self.detail_parse,
                            meta={'title': cata_title, 'cata_id': cata_id},
                            dont_filter=True
                        )
            else:
                dataset_crawled += 1

        # 每页10条数据，如果有超过10条数据被爬过，就不再翻页
        if dataset_crawled >= 10:
            return
        else:
            self.page += 1
            self.form_data['start'] = str(self.page * 10)
            yield scrapy.FormRequest(
                url='http://data.jinan.gov.cn/odweb/catalog/catalog.do?method=GetCatalog',
                formdata=self.form_data,
                callback=self.only_unstructured_parse,
                dont_filter=False
            )

    def detail_parse(self, response):
        data = response.xpath('//div[@class="detail-base-list"]/'
                              'div[contains(string(.),"基本信息")]/following-sibling::div/ul/li')
        metadata = {}
        for index in data:
            key = index.xpath('div[1]/text()').extract_first()
            meta_key = toolkit.remove_blanks(key)
            # \r\n\t\t\t\t\t\t\t\t\t\t\t\t\tDec 15, 2019 3:00:49 AM
            value = index.xpath('div[2]/text()').extract_first()
            if value is not None:
                if meta_key == '最后更新' or meta_key == '发布时间':
                    date_en = re.search('\w+\s+\d+,\s+\d{4}', value)
                    if date_en:
                        date_en = date_en.group()
                        meta_val = time.strftime('%Y-%m-%d', time.strptime(date_en, '%b %d, %Y'))
                else:
                    meta_val = toolkit.remove_blanks(value)

            metadata[meta_key] = meta_val if meta_val else None

        # 文件下载页面请求
        yield scrapy.FormRequest(
            url='http://data.jinan.gov.cn/odweb/catalog/catalogDetail.do?method=GetDownLoadInfo',
            formdata={'cata_id': response.meta['cata_id'], 'conf_type': '2', 'file_type': '1,3'},
            callback=self.file_parse,
            meta={'title': response.meta['title'], 'metadata': metadata},
            dont_filter=False
        )

    def file_parse(self, response):
        item = FileItem()
        headers = {
            'Cookie': 'JSESSIONID=F4E13E8461149A15C4005E70035F06D0; '
                      'sub_domain_cokie=cGAxH0hgyYdVvRPb7RCK5A%3D%3D; region_name=%E5%B1%B1%E4%B8%9C%E7%9C%81; '
                      'callbackUrl=http%3A%2F%2Fdata.jinan.gov.cn%2F; wondersLog_sdywtb_sdk=%7B%22persistedTime'
                      '%22%3A1579225924900%2C%22updatedTime%22%3A1579225978574%2C%22sessionStartTime'
                      '%22%3A1579225925628%2C%22sessionReferrer%22%3A%22http%3A%2F%2Fdata.sd.gov.cn%2Fodweb'
                      '%2FsavCookie.htm%3FcallbackUrl%3Dhttp%25253A%2F%2Fdata.jinan.gov.cn%2F%22%2C%22deviceId'
                      '%22%3A%22fb2bec50f4300d352c959d466eb98570-6693%22%2C%22LASTEVENT%22%3A%7B%22eventId%22%3A'
                      '%22wondersLog_pv%22%2C%22time%22%3A1579225978572%7D%2C%22sessionUuid%22%3A6393870329542040%2C'
                      '%22costTime%22%3A%7B%7D%7D; sso_token=K7Ee21tTZGS8v6jGZTI1IQ%3D%3D; uc_nick_name=""; '
                      'get_ticket=d885371e8701bbe2cfbef0c76426977b',
            'Host': 'data.sd.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/79.0.3945.117 Safari/537.36',
            'Upgrade-Insecure-Requests': '1'
        }
        file_list = json.loads(response.body.decode())['data']
        file_urls = []
        file_name = []
        for file in file_list:
            url = 'http://data.sd.gov.cn/odweb/catalog/CatalogDetailDownload.do?method=getFileDownloadAddr&fileId=%s' \
                  % file.get('fileId')
            file_urls.append(url)
            file_name.append(file['fileName'])
        item['file_urls'] = file_urls
        item['headers'] = headers
        item['title'] = response.meta['title']
        item['file_names'] = file_name
        item['metadata'] = response.meta['metadata']
        yield item

