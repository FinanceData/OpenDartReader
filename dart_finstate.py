#-*- coding:utf-8 -*-
# 2020 FinanceData.KR http://financedata.kr fb.com/financedata

import io
import zipfile
import requests
import xml.etree.ElementTree as ET
import pandas as pd

# 3-1 상장기업 재무정보 (단일회사): api/fnlttSinglAcnt.json
# 3-2 상장기업 재무정보 (다중회사): api/fnlttMultiAcnt.json
def finstate(api_key, corp_code, bsns_year, reprt_code='11011'):
    url = 'https://opendart.fss.or.kr/api/'
    url += 'fnlttMultiAcnt.json' if ',' in corp_code else 'fnlttSinglAcnt.json'

    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year':  bsns_year,   # 사업년도
        'reprt_code': reprt_code, # "11011": 사업보고서
    }

    r = requests.get(url, params=params)
    jo = r.json() 
    if 'list' not in jo:
        print(jo)
        print('전자공시의 재무데이터는 2015년 이후 데이터를 제공합니다') if bsns_year < 2015 else print()
        return pd.DataFrame()
    return pd.DataFrame(jo['list'])

# 3-3 재무제표 원본파일(XBRL): api/fnlttXbrl.xml
def finstate_xml(api_key, rcp_no, save_as='finstate_xml.zip', reprt_code='11011'):
    url = 'https://opendart.fss.or.kr/api/fnlttXbrl.xml'
    params = {
        'crtfc_key': api_key,
        'rcept_no': rcp_no,
        'reprt_code': reprt_code, # "11013"=1분기보고서,  "11012"=반기보고서,  "11014"=3분기보고서, "11011"=사업보고서
    }
    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.content)
        status = tree.find('status').text,
        message = tree.find('message').text
        if status != '000':
            raise ValueError({'status': status, 'message': message})
    except ET.ParseError as e:
        pass

    with open(save_as, 'wb') as f:
        f.write(r.content)
    return True

# 3-4 단일회사 전체 재무제표: api/fnlttSinglAcntAll.json
def finstate_all(api_key, corp_code, bsns_year, reprt_code='11011', fs_div='CFS'):
    url = 'https://opendart.fss.or.kr/api/fnlttSinglAcntAll.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year':  bsns_year,   # 사업년도
        'reprt_code': reprt_code, # "11011": 사업보고서
        'fs_div': fs_div, # 'CFS'=연결제무제표, 'OFS'=별도(개별)제무제표
    }

    r = requests.get(url, params=params)
    jo = r.json() 
    if 'list' not in jo:
        print(jo)
        print('전자공시의 재무데이터는 2015년 이후 데이터를 제공합니다') if bsns_year < 2015 else print()
        return pd.DataFrame()
    return pd.DataFrame(jo['list'])

# 3-5 XBRL 표준계정과목체계(계정과목): api/xbrlTaxonomy.json
def xbrl_taxonomy(api_key, sj_div='BS1'):
    url = 'https://opendart.fss.or.kr/api/xbrlTaxonomy.json'
    params = {
        'crtfc_key': api_key,
        'sj_div': sj_div, # "CFS":연결재무제표, "OFS":재무제표
    }
    r = requests.get(url, params=params)
    jo = r.json() 
    if 'list' not in jo:
        print(jo)
        return pd.DataFrame()
    return pd.DataFrame(jo['list'])
