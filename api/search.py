import requests
import zipfile
import io
import json
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from pandas.io.json import json_normalize

# 1. 공시정보 - 공시검색(목록)
def list(api_key, corp_code, start=None, end=None, kind='', kind_detail='', final=True):
    start = datetime(1970, 1, 1) if start==None else pd.to_datetime(start)
    end = datetime.today() if end==None else pd.to_datetime(end)

    url = 'https://opendart.fss.or.kr/api/list.json'
    params = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bgn_de': start.strftime('%Y%m%d'),
        'end_de': end.strftime('%Y%m%d'),
        'last_reprt_at': 'Y' if final else 'N', # 최종보고서 여부
        'pblntf_ty': kind, # 공시유형: 기본값 'A'=정기공시
        'pblntf_detail_ty': kind_detail, # 공시상세유형
        'page_no': 1,
        'page_count': 100,
    }

    r = requests.get(url, params=params)
    try:
        tree = ET.XML(r.content)
        status = tree.find('status').text
        message = tree.find('message').text
        if status != '000':
            raise ValueError({'status': status, 'message': message})
    except ET.ParseError as e:
        pass

    jo = json.loads(r.text)
    if 'list' not in jo:
        return None
    df = json_normalize(jo, 'list')

    # paging
    for page in range(2, jo['total_page']+1):
        params['page_no'] = page
        r = requests.get(url, params=params)
        jo = json.loads(r.text)
        df = df.append(json_normalize(jo, 'list'))

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
    return json.loads(r.text)

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
        company_list.append(json.loads(r.text))
    return company_list

# 1-3. 공시정보 - 공시서류원본파일
def document(api_key, rcp_no):
    url = 'https://opendart.fss.or.kr/api/document.xml'
    params = {
        'crtfc_key': api_key,
        'rcept_no': rcp_no,
    }

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
    info_list = zf.infolist()
    xml_data = zf.read(info_list[0].filename)
    return xml_data.decode('utf8')


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
