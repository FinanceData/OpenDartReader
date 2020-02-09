import requests
import json
from pandas.io.json import json_normalize

def report(api_key, corp_code, key_word, bsns_year, reprt_code='11011'):
    key_word_map = {
        '증자': 'irdsSttus',
        '배당': 'alotMatter',
        '자기주식': 'tesstkAcqsDspsSttus',
        '최대주주': 'hyslrSttus',
        '최대주주변동': 'hyslrChgSttus',
        '소액주주': 'mrhlSttus',
        '임원': 'exctvSttus',
        '직원': 'empSttus',
        '임원개인보수': 'hmvAuditIndvdlBySttus',
        '임원전체보수': 'hmvAuditAllSttus',
        '개인별보수': 'indvdlByPay',
        '타법인출자': 'otrCprInvstmntSttus',
    }

    if key_word not in key_word_map.keys():
        raise ValueError('key_word is invalid: you can use one of ', key_word_map.keys())

    url = "https://opendart.fss.or.kr/api/{}.json".format(key_word_map[key_word])
    params = {
        'crtfc_key': api_key,    # 인증키
        'corp_code': corp_code,   # 회사 고유번호
        'bsns_year': bsns_year,   # 사업년도
        'reprt_code': reprt_code, # 보고서 코드 ("11011"=사업보고서)
    }
    r = requests.get(url, params=params)
    jo = json.loads(r.text)
    
    if 'list' not in jo:
        return None
    return json_normalize(jo, 'list')
