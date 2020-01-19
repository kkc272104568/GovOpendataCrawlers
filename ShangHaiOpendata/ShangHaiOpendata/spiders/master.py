# -*- coding: utf-8 -*-
import json
import re
import logging
import scrapy
from scrapy import Request, FormRequest
from ..items import FileDownloadItem
from ..utils.LastCrawl import LastCrawl
from ..utils.FileSummary import FilesSummary
from lxml import etree
from ..utils import toolkit
import time


class MasterSpider(scrapy.Spider):
    name = 'master'
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Host": "data.sh.gov.cn",
        "Origin": "https://data.sh.gov.cn",
        "Referer": "https://data.sh.gov.cn/view/data-resource/index.html",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    }
    cookies = {
        "FSSBBIl1UgzbN7N443S": "0CIt2CnYqOs8_mMds.uyp6rqP6zqY1a7m2XswAy4ta.eIVq7._JsX3yC0rjX2nZH",
        "AlteonP": "AL2hP8HcHKxJQAFFrZF4TQ$$",
        "FSSBBIl1UgzbN7N443T": "40EnQI_YLUYThndDg.kdpicEupEZdiN5J4YhqfILrbfkQWr84E_7NUIaerTUFYwhSH230LBJQpka6jLpks_FUsIMsfp7mxhCShnEe9qqtoe4SHymQHCoj0g9q2SbDnxtT39dsfDW9GYecSv.F3.7.f1vErYuFEJWjE3m0oB.pQPRk1qXYB.3JQOSel38kwDo5O9cNbaSClNA1g7nlmi2_mIWM5oz6j6tbLmsd6dVRVHWXJLYhEpXfb2465P2dwiP_vU3is53mCf6KE2q2nWMAzuUxBq3Yc_bkHRxi4OF0qfLjBkcvEi5isIPWZDU2_gHa2rjqdLVfGbyOcMiPPJlv5C4n",
    }

    formdata = {
        "appScenarios": "",
        "dataDomain": "",
        "datasetKeyword": "",
        "fieldListKeyword": "",
        "openResType": "",
        "openType": "",
        "orgId": "",
        "pageNum": 1,
        "pageSize": 10,
        "generalScore": "",
        "resourceKeyword": "",
        "sort": "previewCount:desc"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 上次的采集时间，
        self.last_crawl_date = LastCrawl.crawl_time()

    def start_requests(self) -> 'Request':
        url = 'https://data.sh.gov.cn/yys/es/v1/dataset/search'
        yield scrapy.Request(
            url=url,
            method='post',
            body=json.dumps(self.formdata),
            headers=self.headers,
            cookies=self.cookies,
            callback=self.parse_list
        )

    def parse_list(self, response)-> 'FileDownloadItem':
        """
        解析详情页, 采集数据仅有非结构化类型数据
        :param response: 请求详情页后返回的 response
        :return: None
        """
        if response.status != 200:
            logging.info("首页请求不到数据请检查cookies的有效性或者请重试！")
            return
        # 获取数据json格式
        data = json.loads(response.text).get('data')
        # 获取数据的总页数
        total_num = data.get('totalPageNum')
        # 获取当前页
        current_page = data.get('currentPage')
        list_items = data.get('content')
        for item in list_items:
            # 获取数据的更新时间
            update_timestamp = item.get('updateDate')
            datasetName = item.get('datasetName')
            # 如果数据的更新时间大于上次的爬取时间， 则表示数据为新更数据， 需要爬取
            if update_timestamp > self.last_crawl_date:
                # 获取所有的附件信息
                attachment = item.get('dataResources')
                for index, att_item in enumerate(attachment):
                    url = 'https://data.sh.gov.cn/zq/api/download_file/?path={}&sort=doc_type'.format(
                        att_item.get('resId')
                    )
                    file_name = datasetName + '/' +str(index) + '_' + att_item.get('resName')
                    file_download_item = FileDownloadItem()
                    file_download_item['file_urls'] = [url]
                    file_download_item['metadata'] = {
                        "名称": file_name,
                        "headers": self.headers,
                        "cookies": self.cookies,
                    }
                    # yield 文件下载的item，到FilePipeline中去下载文件
                    yield file_download_item
            else:
                logging.info("后续数据的更新时间小于上次采集时间，数据已经采集过, 停止采集！")
                return None

        # 翻页处理
        if current_page == total_num:
            return
        else:
            url = 'https://data.sh.gov.cn/yys/es/v1/dataset/search'
            self.formdata['pageNum'] = current_page + 1
            yield scrapy.Request(
                url=url,
                method='post',
                body=json.dumps(self.formdata),
                headers=self.headers,
                cookies=self.cookies,
                callback=self.parse_list
            )
