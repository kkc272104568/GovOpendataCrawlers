#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : LastCrawl.py
# @Time    : 2020-1-15 17:16
# @Software: PyCharm
# @Author  : Taoz
# @contact : 371956576@qq.com
# 上一次爬虫情况
import json
import time


class LastCrawl(object):
    FILE = 'last_crawl.json'

    @classmethod
    def get(cls, key):
        with open(cls.FILE, 'r', encoding='utf8') as f:
            item = json.load(f)
            return item[key]

    @classmethod
    def crawl_time(cls) -> int:
        return cls.get('crawl_time')

    @classmethod
    def total_file_size_mb(cls) -> float:
        return cls.get('total_file_size_mb')

    @classmethod
    def dataset_count(cls) -> int:
        return cls.get('dataset_count')

    @classmethod
    def write(cls, dataset_count: int, total_file_size_mb: float):
        with open(cls.FILE, 'w', encoding='utf8') as f:
            json.dump({
                "crawl_time": int(time.time()),
                "dataset_count": dataset_count,
                "total_file_size_mb": total_file_size_mb,
            }, f, ensure_ascii=False)