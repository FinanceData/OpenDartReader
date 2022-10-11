#-*- coding:utf-8 -*-
# 2022 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import json
import pandas as pd
from datetime import datetime, timedelta

def event(api_key, corp_code, key_word, start=None, end=None):
    start = pd.to_datetime(start) if start else pd.to_datetime('1900-01-01')
    end = pd.to_datetime(end) if end else datetime.today()

    key_word_map = {
        '부도발생': 'dfOcr', # 부도발생 
        '영업정지': 'bsnSp', # 영업정지 
        '회생절차': 'ctrcvsBgrq', #  회생절차 개시신청
        '해산사유': 'dsRsOcr', #  해산사유 발생 
        '유상증자': 'piicDecsn', #  유상증자 결정  
        '무상증자': 'fricDecsn', #  무상증자 결정 
        '유무상증자': 'pifricDecsn', #  유무상증자 결정
        '감자': 'crDecsn', #  감자 결정 
        '관리절차개시': 'bnkMngtPcbg', #  채권은행 등의 관리절차 개시 
        '소송': 'lwstLg', #  소송 등의 제기
        '해외상장결정': 'ovLstDecsn', #  해외 증권시장 주권등 상장 결정
        '해외상장폐지결정': 'ovDlstDecsn', #  해외 증권시장 주권등 상장폐지 결정
        '해외상장': 'ovLst', #  해외 증권시장 주권등 상장
        '해외상장폐지': 'ovDlst', #  해외 증권시장 주권등 상장폐지
        '전환사채발행': 'cvbdIsDecsn', #  전환사채권 발행결정
        '신주인수권부사채발행': 'bdwtIsDecsn', #  신주인수권부사채권 발행결정
        '교환사채발행': 'exbdIsDecsn', #  교환사채권 발행결정
        '관리절차중단': 'bnkMngtPcsp', #  채권은행 등의 관리절차 중단
        '조건부자본증권발행': 'wdCocobdIsDecsn', #  상각형 조건부자본증권 발행결정
        '자산양수도': 'astInhtrfEtcPtbkOpt', #  자산양수도(기타), 풋백옵션
        '타법인증권양도': 'otcprStkInvscrTrfDecsn', #  타법인 주식 및 출자 증권 양도결정
        '유형자산양도': 'tgastTrfDecsn', #  유형자산 양도 결정 
        '유형자산양수': 'tgastInhDecsn', #  유형자산 양수 결정
        '타법인증권양수': 'otcprStkInvscrInhDecsn', #  타법인 주식 및 출자증권 양수결정
        '영업양도': 'bsnTrfDecsn', #  영업양도 결정 
        '영업양수': 'bsnInhDecsn', #  영업양수 결정
        '자기주식취득신탁계약해지': 'tsstkAqTrctrCcDecsn', #  자기주식취득 신탁계약 해지 결정
        '자기주식취득신탁계약체결': 'tsstkAqTrctrCnsDecsn', #  자기주식취득 신탁계약 체결 결정
        '자기주식처분': 'tsstkDpDecsn', #  자기주식 처분 결정
        '자기주식취득': 'tsstkAqDecsn', #  자기주식 취득 결정
        '주식교환': 'stkExtrDecsn', #  주식교환·이전 결정
        '회사분할합병': 'cmpDvmgDecsn', #  회사분할합병 결정
        '회사분할': 'cmpDvDecsn', #  회사분할 결정
        '회사합병': 'cmpMgDecsn', #  회사합병 결정
        '사채권양수': 'stkrtbdInhDecsn', #  주권 관련 사채권 양수 결정
        '사채권양도결정': 'stkrtbdTrfDecsn', #  주권 관련 사채권 양도 결정
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
    
    if jo['status'] != '000' or 'list' not in jo:
        print(jo)
        return pd.DataFrame()
    return pd.DataFrame(jo['list'])
