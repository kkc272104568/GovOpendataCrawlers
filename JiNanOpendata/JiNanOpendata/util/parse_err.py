from scrapy.http import Response
import logging
ERR_WORDS = {
    'NO_LIST': '[*** NO LIST DATA ERROR ***] list: {name}: {alias_cn}'
               ' | error url: {url} | response header: {response_headers}',
    'NO_REQUIRED': '[*** NO REQUIRED DATA ERROR ***] required data: {name}: {alias_cn}'
                   ' | error url: {url} | response header: {response_headers}'
}
NO_LIST = 'NO_LIST'
NO_REQUIRED = 'NO_REQUIRED'

def log(err_type, name, alias_cn, response):
    '''
    生成错误报告
    :param err_type: str 错误类型
    :param name: 错误英文名
    :param alias_cn: 错误中文名
    :param response: 当前response
    :return:
    '''
    if not isinstance(response, Response):
        logging.log(logging.ERROR
                    , '[*** TYPE ERROR ***] parse_err.py function log()\'s param response\'s type is not Response')
        return
    err_word = ERR_WORDS.get(err_type).format(name=name, alias_cn=alias_cn, url=response.url, response_headers=response.headers)
    logging.error(err_word)


