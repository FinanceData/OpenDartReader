# OpenDartReader

<img width="40%" src="https://i.imgur.com/FMsL0id.png" >

`OpenDartReader`는 금융감독원 전자공시 시스템의 "Open DART"서비스 API를 손쉽게 사용할 수 있도록 돕는 오픈소스 라이브러리 입니다.


##  OpenDartReader
`Open DART`는 금융감독원이 제공하는 전자공시 시스템에서 제공하는 API서비스 입니다. 기존의 "오픈API", "공시정보 활용마당" 서비스 확대개편하였으며 2020-01-21 (시범) 서비스 시작하였습니다.

`Open DART` API는 매우 잘 만들어진 서비스입니다. 하지만, API를 직접사용하면 추가적인 작업들이 필요합니다. 예를 들어, `Open DART` API는 기업에 대한 내용을 조회할 때, 전자공시에서 사용하는 개별 기업의 고유 번호를 사용합니다. 특정 회사를 상장회사 종목코드으로 조회하려면 매번 고유번호를 얻어야 합니다. 수신한 데이터는 JSON혹은 XML형태 인데 대부분의 경우 pandas 데이터프레임(DataFrame)으로 가공해야 사용하기 더 편리합니다.

`OpenDartReader`는 `Open DART`를 이런 내용을 일반화하고 좀 더 쉽게 `Open DART`를 사용하기 위한 파이썬 라이브러리 입니다. 


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

# API KEY 를 지정하여 OpenDartReader 객체 생성
api_key = 'd81e18ac719d1c1e4ec7899ef21a737ab6cbb4c7' # (이 API-KEY 예제 입니다. 별도 발급받으세요)
dart = OpenDartReader(api_key)

# 삼성전자의 정기보고서('A') 2019년
dart.list(code='005930', kind='A', start='2019-01-01', end='2019-12-31')

# 삼성전자의 모든 공시 리스트 (1999년 ~ 현재)
dart.list('005930') 

# 기업의 개황정보
dart.company('005930')

# 회사명에 삼성전자가 포함된 회사들에 대한 개황정보
dart.company_by_name('삼성전자')

# 삼성전자 사업보고서 (2018.12) 원문 텍스트
xml_text = dart.document('20190401004781')

# 삼성전자(005930), 배당관련 사항, 2018년
dart.report('005930', '배당', 2018) 

# 서울반도체(046890), 최대주주 관한 사항, 2018년
dart.report('046890', '최대주주', 2018) 

# 서울반도체(046890), 임원 관한 사항, 2018년
dart.report('046890', '임원', 2018) 

# 삼성전자 2018 재무제표
dart.finstate('삼성전자', 2018) # 사업보고서

# 삼성전자 2018Q1 재무제표
dart.finstate('삼성전자', 2018, reprt_code='11013')
```

## more information
* [Users Guide (사용자 안내서)]( https://nbviewer.jupyter.org/github/FinanceData/OpenDartReader/blob/master/docs/OpenDartReader_users_guide.ipynb) 
* [Reference Manual (레퍼런스 메뉴얼)]( https://nbviewer.jupyter.org/github/FinanceData/OpenDartReader/blob/master/docs/OpenDartReader_reference_manual.ipynb) 


#### 2020 [FinanceData.KR](http://financedata.kr) | [facebook.com/financedata](http://facebook.com/financedata)
