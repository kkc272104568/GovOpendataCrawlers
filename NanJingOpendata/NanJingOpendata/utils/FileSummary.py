#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Evan
# Date: 2020/1/19

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