#-*- coding:utf-8 -*-
# 2020-2022 FinanceData.KR http://financedata.kr fb.com/financedata

import os
import re
import time
from datetime import datetime
from pandas import to_datetime
from urllib.parse import urlparse, parse_qs, quote_plus
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import difflib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.3904.108 Safari/537.36'

def _validate_dates(start, end):
    start = to_datetime(start)
    end = to_datetime(end)

    if start is None:
        start = datetime(1970, 1, 1)
    if end is None:
        end = datetime.today()
    return start, end

def _requests_get_cache(url, headers=None):
    docs_cache_dir = 'docs_cache'
    if not os.path.exists(docs_cache_dir):
        os.makedirs(docs_cache_dir)
    
    fn = os.path.join(docs_cache_dir, quote_plus(url))
    if not os.path.isfile(fn) or os.path.getsize(fn) == 0:
        with open(fn, 'wt') as f:
            r = requests.get(url, headers=headers)
            f.write(r.text)
            xhtml_text = r.text
    else:
        with open(fn, 'rt') as f:
            xhtml_text = f.read()
            return xhtml_text
    return xhtml_text

      
def list_date_ex(date=None, cache=True):
    '''
    지정한 날짜의 보고서의 목록 전체를 데이터프레임으로 반환 합니다(시간 포함)
    * date: 조회일 (기본값: 당일)
    '''
    date = pd.to_datetime(date) if date else datetime.today() 
    date_str = date.strftime('%Y.%m.%d')

    columns = ['rcept_dt', 'corp_cls', 'corp_name', 'rcept_no', 'report_nm', 'flr_nm', 'rm']
   
    df_list = []
    for page in range(1, 100):
        time.sleep(0.1)
        url = f'http://dart.fss.or.kr/dsac001/search.ax?selectDate={date_str}&pageGrouping=A&currentPage={page}'
        headers = {'User-Agent': USER_AGENT}
        xhtml_text = _requests_get_cache(url, headers=headers) if cache else requests.get(url, headers).text

        if '검색된 자료가 없습니다' in xhtml_text:
            if page == 1:
                return pd.DataFrame(columns=columns)
            break

        data_list = []
        soup = BeautifulSoup(xhtml_text, features="lxml")
        trs = soup.table.tbody.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            hhmm = tds[0].text.strip()
            corp_class = tds[1].span.span.text
            name = tds[1].span.a.text.strip()
            rcp_no = tds[2].a['href'].split('=')[1]
            title = ' '.join(tds[2].a.text.split())
            fr_name = tds[3].text
            rcp_date = tds[4].text.replace('.', '-')
            remark = ''.join([span.text for span in tds[5].find_all('span')])
            dt = date.strftime('%Y-%m-%d') + ' ' + hhmm
            data_list.append([dt, corp_class, name, rcp_no, title, fr_name, remark])

        df = pd.DataFrame(data_list, columns=columns)
        df['rcept_dt'] = pd.to_datetime(df['rcept_dt'])
        df_list.append(df)
    merged = pd.concat(df_list)
    merged = merged.reset_index(drop=True)
    return merged


def sub_docs(rcp_no, match=None):
    '''
    지정한 URL문서에 속해있는 하위 문서 목록정보(title, url)을 데이터프레임으로 반환합니다
    * rcp_no: 접수번호를 지정합니다. rcp_no 대신 첨부문서의 URL(http로 시작)을 사용할 수 도 있습니다.
    * match: 매칭할 문자열 (문자열을 지정하면 문서 제목과 가장 유사한 순서로 소트 합니다)
    '''
    if rcp_no.isdecimal():
        r = requests.get(f'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}', headers={'User-Agent': USER_AGENT})
    elif rcp_no.startswith('http'):
        r = requests.get(rcp_no, headers={'User-Agent': USER_AGENT})
    else:
        raise ValueError('invalid `rcp_no`(or url)')
        
    ## 하위 문서 URL 추출
    multi_page_re = (
        r"\s+node[12]\['text'\][ =]+\"(.*?)\"\;" 
        r"\s+node[12]\['id'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['rcpNo'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['dcmNo'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['eleId'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['offset'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['length'\][ =]+\"(\d+)\";"
        r"\s+node[12]\['dtd'\][ =]+\"(.*?)\";"
        r"\s+node[12]\['tocNo'\][ =]+\"(\d+)\";"
    )
    matches = re.findall(multi_page_re, r.text)
    if len(matches) > 0:
        row_list = []
        for m in matches:
            doc_id = m[1]
            doc_title = m[0]
            params = f'rcpNo={m[2]}&dcmNo={m[3]}&eleId={m[4]}&offset={m[5]}&length={m[6]}&dtd={m[7]}'
            doc_url = f'http://dart.fss.or.kr/report/viewer.do?{params}'
            row_list.append([doc_title, doc_url])
        df = pd.DataFrame(row_list, columns=['title', 'url'])
        if match:
            df['similarity'] = df['title'].apply(lambda x: difflib.SequenceMatcher(None, x, match).ratio())
            df = df.sort_values('similarity', ascending=False)
        return df[['title', 'url']]
    else:
        single_page_re = r"\t\tviewDoc\('(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\S+)',''\)\;"
        matches = re.findall(single_page_re, r.text)
        if len(matches) > 0:
            doc_title = BeautifulSoup(r.text, features="lxml").title.text.strip()
            m = matches[0]
            params = f'rcpNo={m[0]}&dcmNo={m[1]}&eleId={m[2]}&offset={m[3]}&length={m[4]}&dtd={m[5]}'
            doc_url = f'http://dart.fss.or.kr/report/viewer.do?{params}'
            return pd.DataFrame([[doc_title, doc_url]], columns=['title', 'url'])
        else:
            raise Exception(f'{url} 하위 페이지를 포함하고 있지 않습니다')
        
    return pd.DataFrame(None, columns=['title', 'url'])
       

def attach_docs(rcp_no, match=None):
    '''
    첨부문서의 목록정보(title, url)을 데이터프레임으로 반환합니다. match를 지정하면 지정한 문자열과 가장 유사한 순서로 소트하여 데이터프레임을 반환 합니다.
    * rcp_no: 접수번호
    * match: 문서 제목과 가장 유사한 순서로 소트
    '''
    r = requests.get(f'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}', headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, features="lxml")

    row_list = []
    att = soup.find(id='att')
    if not att:
        raise Exception(f'rcp_no={rcp_no} 첨부문서를 포함하고 있지 않습니다')

    for opt in att.find_all('option'):
        if opt['value'] == 'null':
            continue
        title = ' '.join(opt.text.split())
        url = f'http://dart.fss.or.kr/dsaf001/main.do?{opt["value"]}'
        row_list.append([title, url])
        
    df = pd.DataFrame(row_list, columns=['title', 'url'])
    if match:
        df['similarity'] = df.title.apply(lambda x: difflib.SequenceMatcher(None, x, match).ratio())
        df = df.sort_values('similarity', ascending=False)
    return df[['title', 'url']].copy()


def attach_files(arg): # rcp_no or URL
    '''
    접수번호(rcp_no)에 속한 첨부파일 목록정보를 dict 형식으로 반환합니다.
    * rcp_no: 접수번호를 지정합니다. rcp_no 대신 첨부문서의 URL(http로 시작)을 사용할 수 도 있습니다.
    '''
    url= arg if arg.startswith('http') else f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={arg}"
    r = requests.get(url, headers={'User-Agent': USER_AGENT})

    rcp_no = dcm_no = None
    matches = re.findall(
        r"\s+node[12]\['rcpNo'\][ =]+\"(\d+)\";"
     + r"\s+node[12]\['dcmNo'\][ =]+\"(\d+)\";", r.text)
    if matches:
        rcp_no = matches[0][0]
        dcm_no = matches[0][1]

    if not dcm_no:
        print(f'{url} does not have download page. 다운로드 페이지를 포함하고 있지 않습니다.')

    download_url = f'http://dart.fss.or.kr/pdf/download/main.do?rcp_no={rcp_no}&dcm_no={dcm_no}'
    r = requests.get(download_url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find('table')
    if not table:
        return dict()

    attach_files_dict = {}
    for tr in table.tbody.find_all('tr'):
        tds = tr.find_all('td')
        fname = tds[0].text
        flink = 'http://dart.fss.or.kr' + tds[1].a['href']
        attach_files_dict[fname] = flink
    return attach_files_dict


def download(url, fn=None):
    fn = fn if fn else url.split('/')[-1]
    r = requests.get(url, stream=True, headers={'User-Agent': USER_AGENT})
    if r.status_code != 200:
        print(r.status_code)
        return None

    with open(fn, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            f.write(chunk) if chunk else None
    return fn

def list_presenter(presenter, start=None, end=None, report_type='지분공시', final=True):
    '''
    * presenter: 제출자
    * report_type: 보고서 유형
        * "정기공시","주요사항보고", "발행공시", "지분공시", "기타공시", "외부감사관련", 
        * "펀드공시", "자산유동화", "거래소공시", "공정위공시"
    * start: 시작일
    * end: 종료일
    * final: 최종 여부
    '''

    # 시작일, 종료일이 없으면 당일부터 이전 1년으로 설정
    if start is None:
        start = (datetime.today() - timedelta(days=365)).strftime('%Y%m%d')
    if end is None:
        end = datetime.today().strftime('%Y%m%d')

    report_type_value = []
    if report_type == '정기공시':
        report_type_value = '&'.join(['A001', 'A002', 'A003'])
    elif report_type == '주요사항보고':
        report_type_value = '&'.join(['B001', 'B002', 'B003'])
    elif report_type == '발행공시':
        report_type_value = '&'.join(['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008', 'C009', 'C010', 'C011'])
    elif report_type == '지분공시':
        report_type_value = '&'.join(['D001', 'D002', 'D003', 'D004', 'D005'])
    elif report_type == '기타공시':
        report_type_value = '&'.join(['E001', 'E002', 'E003', 'E004', 'E005', 'E006', 'E007', 'E008', 'E009'])
    elif report_type == '외부감사관련':
        report_type_value = '&'.join(['F001', 'F002', 'F003', 'F004'])
    elif report_type == '펀드공시':
        report_type_value = '&'.join(['G001', 'G002', 'G003'])
    elif report_type == '자산유동화':
        report_type_value = '&'.join(['H001', 'H002', 'H003', 'H004', 'H005', 'H006'])
    elif report_type == '거래소공시':
        report_type_value = '&'.join(['I001', 'I002', 'I003', 'I004', 'I005', 'I006'])
    elif report_type == '공정위공시':
        report_type_value = '&'.join(['J001', 'J002', 'J004', 'J005', 'J006'])

    start = pd.to_datetime(start).strftime('%Y%m%d')
    end = pd.to_datetime(end).strftime('%Y%m%d')
    
    url = 'https://dart.fss.or.kr/dsab007/detailSearch.ax'
    columns = ['rcept_dt', 'corp_cls', 'corp_code', 'corp_name', 'rcept_no', 'report_nm', 'presenter', 'rm']
    df_list = []
    
    headers = {'User-Agent': USER_AGENT}
    
    for page in range(1, 100):
        time.sleep(0.1)
        data = {
            'currentPage': str(page),
            'maxResults': '100',
            'maxLinks': '10',
            'sort': 'date',
            'series': 'desc',
            'reportNamePopYn': 'Y',
            'businessCode': 'all',
            'autoSearch': 'N',
            'option': 'corp',
            'textPresenterNm': presenter,
            'startDate': start,
            'endDate': end,
            'finalReport': 'recent' if final else '',
            'businessNm': '전체',
            'corporationType': 'all',
            'closingAccountsMonth': 'all',
        }
        
        if report_type_value:
            data['publicType'] = report_type_value.split('&') if isinstance(report_type_value, str) else report_type_value

        r = requests.post(url, data=data, headers=headers, verify=False)
        
        if '검색된 자료가 없습니다' in r.text or '결과가 없습니다' in r.text:
            if page == 1:
                return pd.DataFrame(columns=columns)
            break
            
        soup = BeautifulSoup(r.text, features="lxml")
        tbody = soup.find('tbody')
        if not tbody:
            break
            
        trs = tbody.find_all('tr')
        if not trs:
            break
            
        data_list = []
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 6:
                continue
                
            corp_class_tag = tds[1].find('span', class_=re.compile(r'tagCom_'))
            corp_class = corp_class_tag['title'].replace('시장', '') if corp_class_tag else ''
            
            a_tag = tds[1].find('a')
            corp_code = ''
            if a_tag and 'openCorpInfoNew' in a_tag.get('href', ''):
                corp_code = a_tag['href'].split("'")[1]
            corp_name = a_tag.text.strip() if a_tag else ''
            
            rcp_no_tag = tds[2].find('a')
            rcp_no = rcp_no_tag['href'].split('=')[1] if rcp_no_tag and '=' in rcp_no_tag['href'] else ''
            report_nm = rcp_no_tag.text.strip() if rcp_no_tag else ''
            
            pres = tds[3].text.strip()
            rcept_dt = tds[4].text.strip().replace('.', '-')
            remark = tds[5].text.strip()
            
            data_list.append([rcept_dt, corp_class, corp_code, corp_name, rcp_no, report_nm, pres, remark])
            
        df = pd.DataFrame(data_list, columns=columns)
        df['rcept_dt'] = pd.to_datetime(df['rcept_dt'])
        df_list.append(df)
        
        page_info = soup.find('div', class_='pageInfo')
        if page_info:
            m = re.search(r'\[(\d+)/(\d+)\]', page_info.text)
            if m:
                curr_page = int(m.group(1))
                total_pages = int(m.group(2))
                if curr_page >= total_pages:
                    break
        else:
            break

    if df_list:
        return pd.concat(df_list).reset_index(drop=True)
    return pd.DataFrame(columns=columns)
