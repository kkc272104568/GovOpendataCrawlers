#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Evan
# Date: 2020/1/19
from scrapy.utils.response import get_base_url
from urllib.parse import urljoin


def unify_url(url, response):
    """
    标准化url路径 （绝对路径和相对路径都会转换成绝对路径）
    :param response: scrapy.Response
    :param url: url
    :return:
    """
    return urljoin(get_base_url(response), url)