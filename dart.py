#-*- coding:utf-8 -*-
# 2020 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import zipfile
import io
import json
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from pandas.io.json import json_normalize
from . import dart_search
from . import dart_report
from . import dart_finstate
from . import dart_share
from . import _utils

class OpenDartReader():
    # init corp_codes (회사 고유번호 데이터)
    def __init__(self, api_key):
        self.corp_codes = dart_search.corp_codes(api_key)
        self.api_key = api_key
        
    # 1-1. 공시정보 - 공시검색(목록)
    def list(self, corp, start=None, end=None, kind='', kind_detail='', final=True):
        '''
        DART 보고서의 목록을 DataFrame으로 반환
        * corp: 종목코드 (고유번호, 법인명도 가능)
        * start: 조회 시작일 (기본값: 1999-01-01')
        * end: 조회 종료일 (기본값: 당일)
        * kind: 보고서 종류:  A=정기공시, B=주요사항보고, C=발행공시, D=지분공시, E=기타공시, 
                                        F=외부감사관련, G=펀드공시, H=자산유동화, I=거래소공시, J=공정위공시
        * final: 최종보고서 여부 (기본값: False)
        '''
        corp_code = self.find_corp_code(corp)
        if not corp_code:
            raise ValueError('could not find "{}"'.format(code))
        return dart_search.list(self.api_key, corp_code, start, end, kind, kind_detail, final)

    # utils: list_date 특정 날짜의 공시보고서 전체
    def list_date(self, date=None, final=True):
        return _utils.list_date(date, final)
        
    # utils: list_date 특정 날짜의 공시보고서 전체 (시간포함)
    def list_date_ex(self, date=None):
        return _utils.list_date_ex(date)

    # 1-2. 공시정보 - 기업개황
    def company(self, corp):
        corp_code = self.find_corp_code(corp)
        return dart_search.company(self.api_key, corp_code)

    # 1-2. 공시정보 - 기업개황 회사명
    def company_by_name(self, name):
        df = self.corp_codes[self.corp_codes['corp_name'].str.contains(name)]
        corp_code_list = list(df['corp_code'])
        return dart_search.company_by_name(self.api_key, corp_code_list)
    
    # 1-3. 공시정보 - 공시서류원본파일
    def document(self, rcp_no):
        return dart_search.document(self.api_key, rcp_no)

    # utils: subdocument list: 하위문서 제목과 URL (tuple list)
    def sub_docs(self, s):
        return _utils.sub_docs(s)

    # utils: sub document list: 하위문서 제목과 URL (tuple list)
    def attach_docs(self, s):
        return _utils.attach_docs(s)
    
    # utils: attach files url list: 첨부파일 URLs (str list)
    def attach_files(self, s):
        return _utils.attach_files(s)
    
    # 1-4. 공시정보 - 고유번호: corp(종목코드 혹은 회사이름) to 고유번호(corp_code)
    def find_corp_code(self, corp):
        if not corp.isdigit():
            df = self.corp_codes[self.corp_codes['corp_name'] == corp]
        elif corp.isdigit() and len(corp) == 6:
            df = self.corp_codes[self.corp_codes['stock_code'] == corp]
        else:
            df = self.corp_codes[self.corp_codes['corp_code'] == corp]
        return None if df.empty else df.iloc[0]['corp_code']

    # 2. 사업보고서 
    def report(self, corp, key_word, bsns_year, reprt_code='11011'):
        corp_code = self.find_corp_code(corp)
        return dart_report.report(self.api_key, corp_code, key_word, bsns_year, reprt_code)

    # 3. 상장기업 재무정보
    def finstate(self, corp, bsns_year, reprt_code='11011'):
        corp_code = self.find_corp_code(corp)
        return dart_finstate.finstate(self.api_key, corp_code, bsns_year, reprt_code)

    # 4-1. 지분공시 - 대량보유 상황보고
    def major_shareholders(self, corp):
        corp_code = self.find_corp_code(corp)
        return dart_share.major_shareholders(self.api_key, corp_code)

    # 4-2. 지분공시 - 임원ㆍ주요주주 소유보고
    def major_shareholders_exec(self, corp):
        corp_code = self.find_corp_code(corp)
        return dart_share.major_shareholders_exec(self.api_key, corp_code)
