#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : FileSummary.py
# @Time    : 2020-1-15 17:17
# @Software: PyCharm
# @Author  : Taoz
# @contact : 371956576@qq.com
# 文件下载情况
import os


class FilesSummary(object):
    FILES = 'files'

    @classmethod
    def size_byte(cls) -> int:
        size = 0
        for root, dirs, files in os.walk(cls.FILES):
            size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size

    @classmethod
    def size_mb(cls) -> float:
        return round(cls.size_byte() / 1024 / 1024, 2)

    @classmethod
    def dataset_count(cls) -> int:
        for root, dirs, files in os.walk(cls.FILES):
            return len(dirs)