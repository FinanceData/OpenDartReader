#-*- coding:utf-8 -*-
# 2020 FinanceData.KR http://financedata.kr fb.com/financedata

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

try:
    from pandas import json_normalize
except ImportError:
    from pandas.io.json import json_normalize
    
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'

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

    columns = ['rcept_dt', 'corp_cls', 'corp_code', 'corp_name', 'rcept_no', 'report_nm', 'flr_nm', 'rm']
   
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
        soup = BeautifulSoup(xhtml_text, 'lxml')
        trs = soup.table.find_all('tr')
        for tr in trs[1:]:
            tds = tr.find_all('td')

            hhmm = tds[0].text.strip()
            corp_class = tds[1].img['title'].replace('시장', '') if tds[1].img else ''
            code = tds[1].a['href'].split('=')[1]
            name = tds[1].a.text.strip()
            rcp_no = tds[2].a['href'].split('=')[1]
            title = ' '.join(tds[2].a.text.split())
            fr_name = tds[3].text
            rcp_date = tds[4].text.replace('.', '-')
            remark = ' '.join([img['title'] for img in tds[5].find_all('img')])

            rm_str_list = [ # 비고에서 삭제할 문자열
                '본 공시사항은', 
                '소관임', 
                '본 보고서 제출 후',
                '가 있으니 관련 보고서를 참조하시기 바람',
                '본 보고서는',
                '을 포함한 것임',

            ]
            remark = re.sub('|'.join(rm_str_list), '', remark)
            remark = ' '.join(remark.split())
            dt = date.strftime('%Y-%m-%d') + ' ' + hhmm
            data_list.append([dt, corp_class, code, name, rcp_no, title, fr_name, remark])

        df = pd.DataFrame(data_list, columns=columns)
        df['rcept_dt'] = pd.to_datetime(df['rcept_dt'])
        df_list.append(df)
    return pd.concat(df_list)


def attach_file_list(rcp_no): # rcp_no or URL
    '''
    접수번호(rcp_no)에 속한 첨부파일 목록정보를 데이터프레임으로 반환합니다.
    * rcp_no: 접수번호를 지정합니다. rcp_no 대신 첨부문서의 URL(http로 시작)을 사용할 수 도 있습니다.
    '''
    if rcp_no.startswith('http'):
        download_url = rcp_no
    else:
        url = f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}"
        r = requests.get(url, headers={'User-Agent': USER_AGENT})

        dcm_no = None
        matches = re.findall(f"viewDoc\('{rcp_no}', '(.*)', null, null, null, 'dart3.xsd'\)", r.text)
        if matches:
            dcm_no = matches[0]

        if not dcm_no:
            raise Exception(f'{url} 다운로드 페이지를 포함하고 있지 않습니다')

        download_url = f'http://dart.fss.or.kr/pdf/download/main.do?rcp_no={rcp_no}&dcm_no={dcm_no}'

    r = requests.get(download_url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, 'lxml')
    table = soup.find('table')
    trs = table.find_all('tr')

    row_list = []
    for tr in trs[1:]:
        tds = tr.find_all('td')
        fname = tds[0].text
        flink = 'http://dart.fss.or.kr' + tds[1].a['href']
        matches = re.findall('/pdf/download/(.*).do', flink)
        ftype = matches[0] if matches else None
        row_list.append([fname, flink, ftype])

    return pd.DataFrame(row_list, columns=['file_name', 'url', 'type'])


def attach_doc_list(rcp_no, match=None):
    '''
    첨부문서의 목록정보(title, url)을 데이터프레임으로 반환합니다. match를 지정하면 지정한 문자열과 가장 유사한 순서로 소트하여 데이터프레임을 반환 합니다.
    * rcp_no: 접수번호
    * match: 문서 제목과 가장 유사한 순서로 소트
    '''
    r = requests.get(f'http://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcp_no}', headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, 'lxml')

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
    matches = re.findall("viewDoc\('(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\S+)'\)\;", r.text)
    if not matches:
        raise Exception(f'{url} 하위 페이지를 포함하고 있지 않습니다')

    doc_urls = []
    for m in matches:
        params = f'rcpNo={m[0]}&dcmNo={m[1]}&eleId={m[2]}&offset={m[3]}&length={m[4]}&dtd={m[5]}'
        url = f'http://dart.fss.or.kr/report/viewer.do?{params}'
        doc_urls.append(url)

    ## 하위 문서 제목 추출
    matches = re.findall('text: \"(.*)\",', r.text)
    doc_titles = matches[1:] # '전체' 제외
    if len(doc_titles) == 0: # 1페이지 경우 (본문의 첫 라인)
        title = bs4.BeautifulSoup(r.text, 'lxml').title.text.strip()
        title = ' '.join(title.split())
        doc_titles = [title]

    df = pd.DataFrame(zip(doc_titles, doc_urls), columns=['title', 'url'])
    if match:
        df['similarity'] = df.title.apply(lambda x: difflib.SequenceMatcher(None, x, match).ratio())
        df = df.sort_values('similarity', ascending=False)
    return df[['title', 'url']].copy()


def retrieve(url, fn=None):
    fn = fn if fn else url.split('/')[-1]
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        print(r.status_code)
        return None

    with open(fn, "wb") as f:
        for chunk in r.iter_content(chunk_size=4096):
            f.write(chunk) if chunk else None
    return fn
