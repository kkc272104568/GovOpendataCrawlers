# import requests
# import json
# url = 'https://data.sh.gov.cn/yys/es/v1/dataset/search'
# data = {
#     "appScenarios": "",
#     "dataDomain": "",
#     "datasetKeyword": "",
#     "fieldListKeyword": "",
#     "openResType": "",
#     "openType": "",
#     "orgId": "",
#     "pageNum": 1,
#     "pageSize": 10,
#     "generalScore": "",
#     "resourceKeyword": "",
#     "sort": "previewCount:desc"
# }
#
# res = requests.post(url=url, data=json.dumps(data), headers=header)
# print(res)
# print(res.text)