#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: Evan
# Date: 2020/1/19

import requests

# url = 'http://data.nanjing.gov.cn/dataSearch/szf/condition?'
# data = {
#             'page': '2',
#             'size': '5',
#         }
# res = requests.post(url=url, data=data)
# print(res.text)

aa = "http://data.nanjing.gov.cn/yy/201802/t20180211_5311021.html"
print(aa.split('/t')[0])
