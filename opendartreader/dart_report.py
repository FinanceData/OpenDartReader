#-*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata

import requests
import json
import pandas as pd

def report(api_key, corp_code, key_word, bsns_year, reprt_code='11011'):
    key_word_map = {
        '조건부자본증권미상환': 'cndlCaplScritsNrdmpBlce', # 조건부 자본증권 미상환 잔액, ※ 2015년 이후 부터 제공
        '미등기임원보수': 'unrstExctvMendngSttus', # 미등기임원 보수현황
        '회사채미상환': 'cprndNrdmpBlce', # 회사채 미상환 잔액
        '단기사채미상환': 'srtpdPsndbtNrdmpBlce', # 단기사채 미상환 잔액
        '기업어음미상환': 'entrprsBilScritsNrdmpBlce', # 기업어음증권 미상환 잔액
        '채무증권발행': 'detScritsIsuAcmslt', # 채무증권 발행실적
        '사모자금사용': 'prvsrpCptalUseDtls', # 사모자금의 사용내역
        '공모자금사용': 'pssrpCptalUseDtls', # 공모자금의 사용내역
        '임원전체보수승인': 'drctrAdtAllMendngSttusGmtsckConfmAmount', # 이사·감사 전체의 보수현황(주주총회 승인금액)
        '임원전체보수유형': 'drctrAdtAllMendngSttusMendngPymntamtTyCl', # 이사·감사 전체의 보수현황(보수지급금액 - 유형별)
        '주식총수': 'stockTotqySttus', # 주식의 총수 현황
        '회계감사': 'accnutAdtorNmNdAdtOpinion', # 회계감사인의 명칭 및 감사의견
        '감사용역': 'adtServcCnclsSttus', # 감사용역체결현황
        '회계감사용역계약': 'accnutAdtorNonAdtServcCnclsSttus', # 회계감사인과의 비감사용역 계약체결 현황
        '사외이사': 'outcmpnyDrctrNdChangeSttus', # 사외이사 및 그 변동현황
        '신종자본증권미상환': 'newCaplScritsNrdmpBlce', # 신종자본증권 미상환 잔액
        '증자': 'irdsSttus', # 증자(감자) 현황
        '배당': 'alotMatter', # 배당에 관한 사항
        '자기주식': 'tesstkAcqsDspsSttus', # 자기주식 취득 및 처분 현황
        '최대주주': 'hyslrSttus', # 최대주주 현황
        '최대주주변동': 'hyslrChgSttus', # 최대주주 변동현황
        '소액주주': 'mrhlSttus', # 소액주주 현황
        '임원': 'exctvSttus', # 임원 현황
        '직원': 'empSttus', # 직원 현황
        '임원개인보수': 'hmvAuditIndvdlBySttus', # 이사·감사의 개인별 보수 현황
        '임원전체보수': 'hmvAuditAllSttus', # 이사·감사 전체의 보수현황
        '개인별보수': 'indvdlByPay', # 개인별 보수지급 금액(5억이상 상위5인)
        '타법인출자': 'otrCprInvstmntSttus', # 타법인 출자현황
    } 

    if key_word not in key_word_map.keys():
        raise ValueError('key_word is invalid: you can use one of ', key_word_map.keys())

    url = f"https://opendart.fss.or.kr/api/{key_word_map[key_word]}.json"
    params = {
        'crtfc_key': api_key,    # 인증키
        'corp_code': corp_code,   # 회사 고유번호
        'bsns_year': bsns_year,   # 사업년도
        'reprt_code': reprt_code, # 보고서 코드 ("11011"=사업보고서)
    }
    r = requests.get(url, params=params)
    jo = r.json()
    
    if jo['status'] != '000' or 'list' not in jo:
        print(jo)
        return pd.DataFrame()
    return pd.DataFrame(jo['list'])
