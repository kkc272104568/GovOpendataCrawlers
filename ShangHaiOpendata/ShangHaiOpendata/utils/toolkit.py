#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @File    : toolkit.py
# @Time    : 2020-1-15 17:15
# @Software: PyCharm
# @Author  : Taoz
# @contact : 371956576@qq.com
# 工具包
import re
import time
import zipfile
from scrapy.utils.response import get_base_url
from urllib.parse import urljoin
from scrapy.http import Response
import logging
import time


def unify_url(response, url):
    """
    标准化url路径 （绝对路径和相对路径都会转换成绝对路径）
    :param response: scrapy.Response
    :param url: url
    :return:
    """
    if not isinstance(response, Response):
        logging.error("[** ERROR **] function unify_path(response, url) "
                      "papram response is not instance of scrapy.Response")
    return urljoin(get_base_url(response), url)


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
    return  int(time.mktime(time_arr))
