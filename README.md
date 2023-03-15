<img width="40%" src="https://i.imgur.com/FMsL0id.png" >

`OpenDartReader`는 금융감독원 전자공시 시스템의 "Open DART"서비스 API를 손쉽게 사용할 수 있도록 돕는 오픈소스 라이브러리 입니다.


##  OpenDartReader
`Open DART`는 금융감독원이 제공하는 전자공시 시스템에서 제공하는 API서비스 입니다. 기존의 "오픈API", "공시정보 활용마당" 서비스 확대개편하였으며 2020-01-21 (시범) 서비스 시작하였습니다.

`Open DART` API는 매우 잘 만들어진 서비스입니다. 하지만, API를 직접사용하면 추가적인 작업들이 필요합니다. 예를 들어, `Open DART` API는 기업에 대한 내용을 조회할 때, 전자공시에서 사용하는 개별 기업의 고유 번호를 사용합니다. 특정 회사를 상장회사 종목코드으로 조회하려면 매번 고유번호를 얻어야 합니다. 수신한 데이터는 JSON혹은 XML형태 인데 대부분의 경우 pandas 데이터프레임(DataFrame)으로 가공해야 사용하기 더 편리합니다.

`OpenDartReader`는 `Open DART`를 이런 내용을 일반화하고 좀 더 쉽게 `Open DART`를 사용하기 위한 파이썬 라이브러리 입니다. 

또한, 부가로 유틸리티 기능으로 하위 문서, 첨부 문서, 첨부 파일, 첨부 파일 다운로드 등을 지원합니다. 예를 들어, 정기 보고서에 포함된 재무제표 엑셀 파일을 손쉽게 다운로드 할 수 있습니다.


## Installation

다음과 같이 설치 합니다.

```bash
pip install opendartreader
```

이미 설치되어 있고 업그레이드가 필요하다면 다음과 같이 설치합니다.
```bash
pip install --upgrade opendartreader 
```

## Quick Start

```python
import OpenDartReader

### 0. 객체 생성 ###
# 객체 생성 (API KEY 지정) 
api_key = 'a81e18ac719d1e1e4ec2899ef25a737ab6cbb4c7'

dart = OpenDartReader(api_key) 


### 1. 공시정보 ###
# 특정기업(삼성전자) 상장이후 모든 공시 목록 (5,600 건+)
dart.list('삼성전자') # 기업이름 혹은,
dart.list('005930') # 종목코드를 사용할 수 있습니다.

# 특정기업(삼성전자) 특정 날짜 이후 공시목록 (날짜에 다양한 포맷이 가능합니다 2022, '2022-01-01', '20220101' )
dart.list('삼성전자', start='2022-01-01') # 2022-01-01 ~ 오늘
dart.list('005930', start='2022-01-01') # 2022-01-01 ~ 오늘

# 특정기업(삼성전자) 특정 일자 범위(start~end)의 공시목록 (날짜에 다양한 포맷이 가능합니다)
dart.list('005930', start='2022-04-28', end='2022-04-28')

# 특정기업(삼성전자) 1999년~이후 모든 정기보고서 (정정된 공시포함)
dart.list('005930', start='1999-01-01', kind='A', final=False)

# 특정기업(삼성전자) 1999년~이후 모든 정기보고서 (최종보고서)
dart.list('005930', start='1999-01-01', kind='A') 

# 2022-07-01 하루동안 모든 기업의 공시목록
dart.list(start='20200701', end='20200701')

# 2022-01-01 ~ 2022-01-10 모든 회사의 모든 공시목록 (3,139 건)
dart.list(start='2022-01-01', end='2022-01-10')

# 2022-01-01 ~ 2022-01-10 모든 회사의 모든 공시목록 (정정된 공시포함) (3,587 건)
dart.list(start='2022-01-01', end='2022-01-10', final=False)

# 2022-01-01~2022-03-30 모든 회사의 정기보고서 (corp를 특정 하지 않으면 최대 3개월) (2,352 건)
dart.list(start='2022-01-01', end='2022-03-30', kind='A')


# ==== 1-2. 공시정보 - 기업개황 ====
# 기업의 개황정보
dart.company('005930')

# 회사명에 "삼성전자"가 포함된 회사들에 대한 개황정보
dart.company_by_name('삼성전자')

# ==== 1-2. 공시정보 - 기업개황 ====
# 기업의 개황정보
dart.company('005930')

# 회사명에 "삼성전자"가 포함된 회사들에 대한 개황정보
dart.company_by_name('삼성전자')


# ==== 1-3. 공시정보 - 공시서류원본파일 ====
# 삼성전자 사업보고서 (2022년 반기사업보고서) 원문 텍스트
xml_text = dart.document('20220816001711')

# ==== 1-3. 공시정보 - 공시서류원본파일 전체 리스트 (사업보고서, 감사보고서) ====
# 삼성전자 사업보고서 (2022년 반기사업보고서) 원문 텍스트, 감사보고서
xml_text_list = dart.document_all('20220816001711')
xml_text = xml_text_list[0]

# ==== 1-4. 공시정보 - 고유번호 ====
# 종목코드로 고유번호 얻기
dart.find_corp_code('005930')

# 기업명으로 고유번호 얻기
dart.find_corp_code('삼성전자')


### 2. 사업보고서 ###
# 조회가능한 사업보고서의 항목: 
['조건부자본증권미상환', '미등기임원보수', '회사채미상환', '단기사채미상환', '기업어음미상환', '채무증권발행', '사모자금사용', '공모자금사용', '임원전체보수승인', '임원전체보수유형', '주식총수', '회계감사', '감사용역', '회계감사용역계약', '사외이사', '신종자본증권미상환', '증자', '배당', '자기주식', '최대주주', '최대주주변동', '소액주주', '임원', '직원', '임원개인보수', '임원전체보수', '개인별보수', '타법인출자']

dart.report('005930', '미등기임원보수', 2021)  # 미등기임원 보수현황
dart.report('005930', '증자', 2021) # 증자(감자) 현황
dart.report('005930', '배당', 2018)  # 배당에 관한 사항


### 3. 상장기업 재무정보 ###
# 상장법인(금융업 제외)의 주요계정과목(재무상태표, 손익계산서)

# 삼성전자 2021 재무제표 
dart.finstate('삼성전자', 2021) 

# 삼성전자 2021Q1 재무제표
dart.finstate('삼성전자', 2021, reprt_code='11013')

# 여러 상장법인(금융업 제외)의 주요계정과목(재무상태표, 손익계산서)
dart.finstate('00126380,00164779,00164742', 2021)
dart.finstate('005930, 000660, 005380', 2021)
dart.finstate('삼성전자, SK하이닉스, 현대자동차', 2021)

# 재무제표 XBRL 원본 파일 저장 (삼성전자 2021 사업보고서)
dart.finstate_xml('20220308000798', save_as='삼성전자_2021_사업보고서_XBRL.zip')

# 전체 재무제표 (삼성전자 2021 전체 재무제표)
dart.finstate_all('005930', 2021)

# XBRL 표준계정과목체계(계정과목)
dart.xbrl_taxonomy('BS1')


### 4. 지분공시 ###
# 대량보유 상황보고 (종목코드, 종목명, 고유번호 모두 지정 가능)
dart.major_shareholders('삼성전자')

# 임원ㆍ주요주주 소유보고 (종목코드, 종목명, 고유번호 모두 지정 가능)
dart.major_shareholders_exec('005930')

### 5. 주요사항보고서  ###
# dart.event(corp, event, start=None, end=None)
# 조회가능한 주요사항 항목: 
# ['부도발생', '영업정지', '회생절차', '해산사유', '유상증자', '무상증자', '유무상증자', '감자', '관리절차개시', '소송', '해외상장결정', '해외상장폐지결정', '해외상장', '해외상장폐지', '전환사채발행', '신주인수권부사채발행', '교환사채발행', '관리절차중단', '조건부자본증권발행', '자산양수도', '타법인증권양도', '유형자산양도', '유형자산양수', '타법인증권양수', '영업양도', '영업양수', '자기주식취득신탁계약해지', '자기주식취득신탁계약체결', '자기주식처분', '자기주식취득', '주식교환', '회사분할합병', '회사분할', '회사합병', '사채권양수', '사채권양도결정']

dart.event('052220', '영업정지', '2019') # iMBC(052220)
dart.event('라이트론', '회생절차', '2019') # 라이트론(069540)
dart.event('휴림네트웍스', '유상증자') # 휴림네트웍스(192410)
dart.event('미원상사', '무상증자') # 미원상사(084990)
dart.event('017810', '전환사채발행') # 풀무원(017810)
dart.event('키다리스튜디오', '신주인수권부사채발행') #  키다리스튜디오(020120) 
dart.event('이스트소프트', '교환사채발행') # 이스트소프트(047560) 


### 6. 증권신고서   ###
# dart.regstate(corp, key_word, start=None, end=None)
# 조회가능한 증권신고서 항목: ['주식의포괄적교환이전', '합병', '증권예탁증권', '채무증권', '지분증권', '분할']

dart.regstate('하림지주', '주식의포괄적교환이전')
dart.regstate('사조대림', '합병')
dart.regstate('에스앤케이', '증권예탁증권')
dart.regstate('BNK금융지주', '채무증권')
dart.regstate('금호전기', '지분증권')
dart.regstate('케이씨씨', '분할')

### 7. 확장 기능   ###
# 지정한 날짜의 공시목록 전체 (공시 시간 정보 포함)
dart.list_date_ex('2022-10-03')

# 하위 문서(sub_docs), 첨부 문서(attach_doc_list)
rcp_no = '20220308000798' 
dart.sub_docs(rcp_no) # 하위 문서 제목과 URL
dart.sub_docs(rcp_no, match='감사의견')  # 제목이 잘 매치되는 순서로 소트
dart.attach_doc_list(rcp_no) # 첨부 문서(i.e. 감사보고서) 제목과 URL
dart.attach_doc_list(rcp_no, match='감사의의견서') # 제목이 잘 매치되는 순서로 소트

# 첨부 파일 제목과 URL
dart.attach_files(rcp_no)

# URL을 지정한 파일로 다운로드
url = 'http://dart.fss.or.kr/pdf/download/excel.do?rcp_no=20220308000798&dcm_no=8446647&lang=ko'
fn = '[삼성전자]사업보고서_재무제표(2022.03.08)_ko.xls'
dart.download(url, fn)

# 첨부파일 모두 다운로드
for k in dart.attach_files('20221111000817'):
    url, fn = atts[k], k
    print(url, fn)
    dart.download(url, fn)
```


## more information
* [Users Guide (사용자 안내서)](https://nbviewer.jupyter.org/github/FinanceData/OpenDartReader/blob/master/docs/OpenDartReader_users_guide.ipynb) 
* [Reference Manual (레퍼런스 메뉴얼)](https://nbviewer.jupyter.org/github/FinanceData/OpenDartReader/blob/master/docs/OpenDartReader_reference_manual.ipynb) 

## tutorials
* [OpenDartReader - 비상장 기업 데이터 조회와 활용 (재무데이터)](https://nbviewer.jupyter.org/12440c298682c44758e4789909a3f333) 
* [OpenDartReader - 현대차 기아차 계속 보유해야 할까 (지분공시)](https://nbviewer.jupyter.org/90f5d24c26648438c792eb9fdb3f6980) 


***2021-2023 [FinanceData.KR]() | [facebook.com/financedata]()***
