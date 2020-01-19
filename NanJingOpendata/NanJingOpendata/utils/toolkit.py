#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Evan
# Date: 2020/1/19

# 工具包
import re
import time
import zipfile


def un_zip(file_name: str, dir_name: str):
    """解压zip文件"""
    zip_file = zipfile.ZipFile(file_name)
    for names in zip_file.namelist():
        zip_file.extract(names, dir_name)
    zip_file.close()


def remove_blanks(s: str) -> str:
    """去掉字符串中的空格"""
    return re.sub('\s+|\n+', '', s)


def date_to_stamp(d: str) -> int:
    """日期转时间戳"""
    time_arr = time.strptime(d, "%Y-%m-%d")
    return int(time.mktime(time_arr))
