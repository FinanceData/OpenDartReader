import io
import zipfile
import requests
import json
from pandas.io.json import json_normalize

def finstate(api_key, corp_code, bsns_year, reprt_code='11011'):
    url = 'https://opendart.fss.or.kr/api/fnlttSinglAcnt.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year':  bsns_year,   # 사업년도
        'reprt_code': reprt_code, # "11011": 사업보고서
    }

    r = requests.get(url, params=params)
    jo = json.loads(r.text)
    if 'list' not in jo:
        return None
    return json_normalize(jo, 'list')
