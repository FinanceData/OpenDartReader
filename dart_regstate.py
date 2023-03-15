#-*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import pandas as pd
from datetime import datetime, timedelta

def regstate(api_key, corp_code, key_word, start=None, end=None):
    start = pd.to_datetime(start) if start else pd.to_datetime('1900-01-01')
    end = pd.to_datetime(end) if end else datetime.today()

    key_word_map = {
        '주식의포괄적교환이전': 'extrRs', # 주식의포괄적교환이전
        '합병': 'mgRs', # 합병
        '증권예탁증권': 'stkdpRs', # 증권예탁증권
        '채무증권': 'bdRs', #  채무증권
        '지분증권': 'estkRs', # 지분증권 
        '분할': 'dvRs', #  분할
    } 

    if key_word not in key_word_map.keys():
        raise ValueError('key_word is invalid: you can use one of ', key_word_map.keys())

    url = f"https://opendart.fss.or.kr/api/{key_word_map[key_word]}.json"
    params = {
        'crtfc_key': api_key,    # 인증키
        'corp_code': corp_code,   # 회사 고유번호
        'bgn_de': start.strftime('%Y%m%d'),  # 시작일(최초접수일)
        'end_de': end.strftime('%Y%m%d'), # 종료일(최초접수일)
    }
    r = requests.get(url, params=params)
    jo = r.json()
    
    if jo['status'] != '000':
        print(jo)
        return pd.DataFrame()
    elif 'list' in jo:
        return pd.DataFrame(jo['list'])
    elif 'group' in jo:
        group = pd.DataFrame(jo['group'])
        df_list = []
        for ix, row in group.iterrows():
            inner_df = pd.DataFrame(row['list'])
            inner_df['title'] = row['title']
            df_list.append(inner_df)
        return pd.concat(df_list)
    else:
        print('invalid respose')
        print(jo)
    return pd.DataFrame()


