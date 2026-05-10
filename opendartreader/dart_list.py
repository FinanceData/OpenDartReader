#-*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import zipfile
import io
import os
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

# 1. 공시정보 - 공시검색(목록)
def list(api_key, corp_code='', start=None, end=None, kind='', kind_detail='', final=False):
    start = pd.to_datetime(start) if start else pd.to_datetime('1900-01-01')
    end = pd.to_datetime(end) if end else datetime.today()
    
    url = 'https://opendart.fss.or.kr/api/list.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bgn_de': start.strftime('%Y%m%d'),
        'end_de': end.strftime('%Y%m%d'),
        'last_reprt_at': 'Y' if final else 'N', # 최종보고서 여부
        'page_no': 1,
        'page_count': 100,
    }
    if kind:
        params['pblntf_ty'] = kind # 공시유형: 기본값 'A'=정기공시
    if kind_detail:
        params['pblntf_detail_ty'] = kind_detail

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.content)
        status = tree.find('status').text
        message = tree.find('message').text
        if status != '000':
            raise ValueError({'status': status, 'message': message})
    except ET.ParseError as e:
        jo = r.json()
        if jo['status'] != '000':
            print(ValueError(r.text))

    jo = r.json()
    if 'list' not in jo:
        return pd.DataFrame()
    df = pd.DataFrame(jo['list'])

    # paging
    for page in range(2, jo['total_page']+1):
        params['page_no'] = page
        r = requests.get(url, params=params)
        jo = r.json()
        df = pd.concat([df, pd.DataFrame(jo['list'])])
        df = df.reset_index(drop=True)
    return df


# 1-2. 공시정보 - 기업개황
def company(api_key, corp_code):
    url = 'https://opendart.fss.or.kr/api/company.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
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
    return r.json()

# 1-2. 공시정보 - 기업개황: 지정된 이름(name)을 포함하는 회사들의 corp_code 리스트를 반환
def company_by_name(api_key, corp_code_list):
    url = 'https://opendart.fss.or.kr/api/company.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': '',
    }
    company_list = []
    for corp_code in corp_code_list:
        params['corp_code'] = corp_code
        r = requests.get(url, params=params)
        company_list.append(r.json())
    return company_list

# 1-3. 공시정보 - (사업보고서) 공시서류원본파일 
def document(api_key, rcp_no, cache=True):

    url = 'https://opendart.fss.or.kr/api/document.xml'
    params = {
        'crtfc_key': api_key,
        'rcept_no': rcp_no,
    }

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.text)
        status = tree.find('status').text
        message = tree.find('message').text
        if status != '000':
            raise ValueError({'status': status, 'message': message})
    except ET.ParseError as e:
        pass

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    info_list = zf.infolist()
    fnames = sorted([info.filename for info in info_list])
    xml_data = zf.read(fnames[0])

    try:
        xml_text = xml_data.decode('euc-kr')
    except UnicodeDecodeError as e:
        xml_text = xml_data.decode('utf-8')
    except UnicodeDecodeError as e:
        xml_text = xml_data

    return xml_text

# 1-3. 공시정보 - (사업보고서, 감사보고서) 공시서류원본문서파일 
def document_all(api_key, rcp_no, cache=True):

    url = 'https://opendart.fss.or.kr/api/document.xml'
    params = {
        'crtfc_key': api_key,
        'rcept_no': rcp_no,
    }

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.text)
        status = tree.find('status').text
        message = tree.find('message').text
        if status != '000':
            raise ValueError({'status': status, 'message': message})
    except ET.ParseError as e:
        pass

    zf = zipfile.ZipFile(io.BytesIO(r.content))
    info_list = zf.infolist()
    fnames = sorted([info.filename for info in info_list])
    xml_text_list = []
    for fname in fnames:
        xml_data = zf.read(fname)
        try:
            xml_text = xml_data.decode('euc-kr')
        except UnicodeDecodeError as e:
            xml_text = xml_data.decode('utf-8')
        except UnicodeDecodeError as e:
            xml_text = xml_data
        xml_text_list.append(xml_text)

    return xml_text_list

# 1-4 고유번호: api/corpCode.xml
def corp_codes(api_key):
        url = 'https://opendart.fss.or.kr/api/corpCode.xml'
        params = { 'crtfc_key': api_key, }

        r = requests.get(url, params=params)
        try:
            tree = ET.XML(r.content)
            status = tree.find('status').text
            message = tree.find('message').text
            if status != '000':
                raise ValueError({'status': status, 'message': message})
        except ET.ParseError as e:
            pass

        zf = zipfile.ZipFile(io.BytesIO(r.content))
        xml_data = zf.read('CORPCODE.xml')

        # XML to DataFrame
        tree = ET.XML(xml_data)
        all_records = []

        element = tree.findall('list')
        for i, child in enumerate(element):
            record = {}
            for i, subchild in enumerate(child):
                record[subchild.tag] = subchild.text
            all_records.append(record)
        return pd.DataFrame(all_records)
