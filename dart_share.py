import requests
import json
import pandas as pd

try:
    from pandas import json_normalize
except ImportError:
    from pandas.io.json import json_normalize

# 대량보유 상황보고
def major_shareholders(api_key, corp_code):
    url = 'https://opendart.fss.or.kr/api/majorstock.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
    }

    r = requests.get(url, params=params)
    jo = json.loads(r.text)
    return json_normalize(jo, 'list')

# 임원ㆍ주요주주 소유보고
def major_shareholders_exec(api_key, corp_code):
    url = 'https://opendart.fss.or.kr/api/elestock.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
    }

    r = requests.get(url, params=params)
    jo = json.loads(r.text)
    if 'list' not in jo:
        return None
    return json_normalize(jo, 'list')
