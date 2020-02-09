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
# from . import finstate
# from . import share

class OpenDartReader():
    # init corp_codes (회사 고유번호 데이터)
    def __init__(self, api_key):
        self.corp_codes = dart_search.corp_codes(api_key)
        self.api_key = api_key
        
    # 1-1. 공시정보 - 공시검색(목록)
    def list(self, corp, start=None, end=None, kind='', kind_detail='', final=True):
        corp_code = self.find_corp_code(corp)
        if not corp_code:
            raise ValueError('could not find "{}"'.format(code))
        return dart_search.list(self.api_key, corp_code, start, end, kind, kind_detail, final)

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
