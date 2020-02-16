#-*- coding:utf-8 -*-
# 2020 FinanceData.KR http://financedata.kr fb.com/financedata

import re
from datetime import datetime
from pandas import to_datetime
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
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

def list_date(date=None, final=True):
    '''
    지정한 날짜의 보고서의 목록 전체를 데이터프레임으로 반환
    * date: 조회일 (기본값: 당일)
    * final: 최종보고서 여부 (기본값: False)
    '''
    date = pd.to_datetime(date) if date else datetime.today()
    dt_str = date.strftime('%Y%m%d')
    fin_rpt = 'Y' if final else 'N' 

    auth = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    headers={
        'Referer':'https://dart.fss.or.kr/dsap001/guide.do', 
        'User-Agent': USER_AGENT }

    url_tmpl = 'http://dart.fss.or.kr/api/search.json?'\
               'page_set=100&auth={auth}&start_dt={start_dt}&end_dt={end_dt}&fin_rpt={fin_rpt}&page_no={page_no}'
    url = url_tmpl.format(auth=auth, start_dt=dt_str, end_dt=dt_str, fin_rpt=fin_rpt, page_no=1)
    r = requests.get(url, headers=headers)
    jo = json.loads(r.text)
    df = json_normalize(jo, 'list')
    
    for page in range(2, jo['total_page']+1):
        url = url_tmpl.format(auth=auth, start_dt=dt_str, end_dt=dt_str, fin_rpt=fin_rpt, page_no=page)
        r = requests.get(url, headers=headers)
        jo = json.loads(r.text)
        df = df.append(json_normalize(jo, 'list'))
        
    cols = {'crp_cd':'corp_code','crp_cls':'corp_cls','crp_nm':'corp_name','flr_nm':'flr_nm',
            'rcp_dt':'rcept_dt','rcp_no':'rcept_no','rmk':'rm','rpt_nm':'report_nm'}
    df.rename(columns=cols, inplace=True)
    if len(df) == 0:
        return df
    df['rcept_dt'] = pd.to_datetime(df['rcept_dt'])
    df.set_index('rcept_dt', inplace=True)
    return df.sort_values('rcept_no')

def list_date_ex(date=None):
    '''
    지정한 날짜의 보고서의 목록 전체를 데이터프레임으로 반환 (시간 포함)
    * date: 조회일 (기본값: 당일)
    '''
    date = pd.to_datetime(date) if date else datetime.today() 
    date_str = date.strftime('%Y.%m.%d')
    url = 'http://dart.fss.or.kr/dsac001/mainAll.do?selectDate=' + date_str
    headers = {
        'Cookie':'DSAC001_MAXRESULTS=10000;', 
        'Referer':'https://dart.fss.or.kr/dsap001/guide.do', 
        'User-Agent': USER_AGENT }
        
    r = requests.get(url, headers=headers)

    columns = ['rcept_dt', 'corp_cls', 'corp_code', 'corp_name', 'rcept_no', 'report_nm', 'flr_nm', 'rm']
    if '검색된 자료가 없습니다' in r.text:
        return pd.DataFrame(columns=columns)

    data_list = []
    soup = BeautifulSoup(r.text, features = "lxml")
    trs = soup.table.find_all('tr')
    for tr in trs[1:]:
        tds = tr.find_all('td')
        시간 = tds[0].text.strip()
        시장 = tds[1].img['title'].replace('시장', '') if tds[1].img else ''
        종목코드 = tds[1].a['href'].split('=')[1]
        종목명 = tds[1].a.text.strip()
        접수번호 = tds[2].a['href'].split('=')[1]
        보고서명 = ' '.join(tds[2].a.text.split())
        제출인 = tds[3].text
        접수일자 = tds[4].text.replace('.', '-')
        비고 = ' '.join([img['title'] for img in tds[5].find_all('img')])
        rm_str_list = [ # 비고에서 삭제할 문자열
            '본 공시사항은', 
            '소관임', 
            '본 보고서 제출 후',
            '가 있으니 관련 보고서를 참조하시기 바람',
            '본 보고서는',
            '을 포함한 것임',
            
        ]
        비고 = re.sub('|'.join(rm_str_list), '', 비고)
        비고 = ' '.join(비고.split())
        날짜 = date.strftime('%Y-%m-%d') + ' ' + 시간
        data_list.append([날짜, 시장, 종목코드, 종목명, 접수번호, 보고서명, 제출인, 비고])
        
    df = pd.DataFrame(data_list, columns=columns)
    df['rcept_dt'] = pd.to_datetime(df['rcept_dt'])
    df.set_index('rcept_dt', inplace=True)
    df.sort_index(inplace=True)
    return df

def sub_docs(s): # rcp_no or URL
    url = s if s.startswith('http') else "http://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(s)

    # 접수번호(rcp_no)에 해당하는 모든 하위 보고서 URL을 추출하여 리스트로 반환
    doc_urls = []
    headers = {
        'Referer':'https://dart.fss.or.kr/dsap001/guide.do', 
        'User-Agent': USER_AGENT }

    r = requests.get(url, headers=headers)

    multi_page_re = "{viewDoc\('(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\S+)'\)\;"
    single_page_re = "\t\tviewDoc\('(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\d+)', '(\S+)'\)\;"
    matches = re.findall(multi_page_re, r.text)
    if len(matches) == 0: 
        matches = re.findall(single_page_re, r.text)

    doc_url_tmpl = "http://dart.fss.or.kr/report/viewer.do?rcpNo=%s&dcmNo=%s&eleId=%s&offset=%s&length=%s&dtd=%s" 
    for m in matches:
        url = doc_url_tmpl % m
        doc_urls.append(url)

    # 접수번호(rcp_no)에 해당하는 모든 하위 보고서의 제목 리스트 반환
    matches = re.findall('text: \"(.*)\",', r.text)
    
    doc_titles = matches[1:] # '전체' 제외
    if len(doc_titles) == 0: # 1페이지 경우 (본문의 첫 라인)
        t = BeautifulSoup(r.text, features = "lxml").title
        title = t.text.strip() if t else '' 
        doc_titles = [title]
    return list(zip(doc_titles, doc_urls))

def attach_docs(s): # rcp_no or URL
    url = s if s.startswith('http') else "http://dart.fss.or.kr/dsaf001/main.do?rcpNo={}".format(s)
    headers = {
        'Referer':'https://dart.fss.or.kr/dsap001/guide.do', 
        'User-Agent': USER_AGENT }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, features = "lxml")
    options = soup.select('#att > option')

    doc_urls = []
    for opt in options:
        if 'rcpNo=' in opt['value']:
            name = ' '.join(opt.text.strip().split())
            url = 'http://dart.fss.or.kr/dsaf001/main.do?' + opt['value']
            row = (name, url)
            doc_urls.append(row)
    return doc_urls

def attach_files(s): # rcp_no or URL
    if s.startswith('http'):
        parts = urlparse(s)
        rcp_no = parse_qs(parts.query)['rcpNo'][0]
        url = s
    else: # s == rcp_no
        rcp_no = s
        url = "http://dart.fss.or.kr/dsaf001/main.do?rcpNo=%s" % (rcp_no)
    
    headers = {
        'Referer':'https://dart.fss.or.kr/dsap001/guide.do', 
        'User-Agent': USER_AGENT }
    r = requests.get(url, headers=headers)

    start_str = "javascript: viewDoc\('" + rcp_no + "', '"
    end_str = "', null, null, null,"
    reg = re.compile(start_str + '(.*)' + end_str)
    m = reg.findall(r.text)
    dcm_no = m[0]

    down_url_tmpl = 'http://dart.fss.or.kr/pdf/download/main.do?rcp_no={}&dcm_no={}'
    down_url = down_url_tmpl.format(rcp_no, dcm_no)
    r = requests.get(down_url, headers=headers)
    soup = BeautifulSoup(r.text, features = "lxml")

    a_list = soup.find_all('a')
    attach_urls = []
    find_list = [
        ('download/excel', 'XLS', 'excel'),
        ('download/pdf', 'PDF', 'pdf'),
        ('download/ifrs', 'ZIP', 'ifrs'),
    ]
    attach_list = []
    url_tmpl = "http://dart.fss.or.kr/pdf/download/{}.do?rcp_no={}&dcm_no={}&lang=ko"
    for a in a_list:
        for find in find_list:
            if find[0] in a['href']:
                row  = (find[1], url_tmpl.format(find[2], rcp_no, dcm_no))
                attach_list.append(row)
    return attach_list
