<img width="40%" src="https://i.imgur.com/FMsL0id.png" >

`OpenDartReader` is an open-source Python library that makes it easier to use the **Open DART** API from the Financial Supervisory Service (FSS) electronic disclosure system (DART).

**Korean documentation:** [README.ko.md](README.ko.md)

## OpenDartReader

**Open DART** is an API offered as part of Korea’s electronic disclosure system. It replaced and expanded the older “Open API” and “Disclosure Information Plaza” services; the pilot opened on 2020-01-21.

The Open DART API is well designed, but using it directly still means extra work: lookups are keyed by each issuer’s **corporation code** (`corp_code`), not only by listed **stock code** (`005930`, etc.). If you query by ticker, you must resolve the corporation code first. Responses are JSON or XML; for analysis you usually want **pandas** `DataFrame`s.

`OpenDartReader` wraps those details so you can pass company names or stock codes where practical. It also adds helpers for sub-documents, attachments, downloads (e.g. financial-statement spreadsheets in periodic reports), and more.

## Quick start (CLI and automation)

### Install and set `DART_API_KEY`

```bash
# Install
uv tool install opendartreader

# Upgrade
uv tool install --upgrade opendartreader
```

Set the API key:

```bash
# Environment variable (Unix/macOS)
export DART_API_KEY="your_api_key_here"
```

On Windows (current session): `set DART_API_KEY=your_api_key_here`

The library loads **`python-dotenv`**: you can put a `.env` file in your project (or run directory) with:

```env
DART_API_KEY="your_api_key_here"
```

### Commands

Short flags: `-s`/`--start`, `-e`/`--end`, `-k`/`--kind`, `-p`/`--pretty`, `-h`/`--help`.

```bash
# Disclosure search (Samsung Electronics). If you omit the date range, the last year through today is used.
dart list "삼성전자"

# From a start date through today — default JSON output
dart list "삼성전자" --start "2024-01-01"

# Fixed range — human-readable table
dart list "삼성전자" --start "2025-01-01" --end "2025-12-31" --pretty

# All companies for a single calendar day
dart list --start "2026-05-04" --end "2026-05-04" --pretty

# Q1 regular disclosures (kind A)
dart list --start "2026-01-01" --end "2026-03-31" --kind "A" --pretty

# Company profile (JSON)
dart company "삼성전자"

# Profile by name substring (may return multiple companies)
dart company-by-name "삼성전자"

# Financial statements (JSON)
dart finstate "삼성전자" 2023

# Several companies
dart finstate "005930, 000660, 005380" 2021
dart finstate "삼성전자, SK하이닉스, 현대자동차" 2025

# Save XBRL package
dart finstate-xml 20220308000798

# Major shareholders
dart shareholders "삼성전자"

# Business report section (e.g. dividends)
dart report "삼성전자" "배당" 2023

# Full disclosure document (.html)
dart document 20220816001711

# All parts of a filing (multiple .html files)
dart document-all 20220816001711

# Sub-document titles and URLs
dart sub-docs 20220308000798
dart sub-docs 20220308000798 --match=감사의견

# Resolve corporation code from ticker or Korean name
dart find-corp-code 005930
dart find-corp-code 삼성전자

# Download all attachments for a receipt number
dart attach-files 20221111000817

# Search by presenter (submitter) name
# --type (Korean labels): "정기공시","주요사항보고", "발행공시", "지분공시", "기타공시", "외부감사관련", "펀드공시", "자산유동화", "거래소공시", "공정위공시"
dart list-presenter 국민연금공단 --start 2026-01-01 --end 2026-04-30 --type 지분공시
dart list-presenter 삼성전자 --start 2026-01-01 --type 주요사항보고
```

## Quick start (library / API)

Install or upgrade:

```bash
pip install opendartreader
pip install --upgrade opendartreader
```

```python
from opendartreader import OpenDartReader

### 0. Client ###
api_key = 'your_api_key_here'
dart = OpenDartReader(api_key)

# Or rely on the environment / .env (variable name DART_API_KEY)
dart = OpenDartReader()


### 1. Disclosures ###
# Last year through today if both start and end are omitted
dart.list('삼성전자')
dart.list('005930')

# From a start date through today (flexible date formats)
dart.list('삼성전자', start='2022-01-01')
dart.list('005930', start='2022-01-01')

# Explicit range
dart.list('005930', start='2022-04-28', end='2022-04-28')

# Periodic reports (kind A), including corrections
dart.list('005930', start='1999-01-01', kind='A', final=False)

# Periodic reports — final reports only (default final=True)
dart.list('005930', start='1999-01-01', kind='A')

# Single day, all companies
dart.list(start='20200701', end='20200701')

# Range, all companies
dart.list(start='2022-01-01', end='2022-01-10')

# Same range, include corrected filings
dart.list(start='2022-01-01', end='2022-01-10', final=False)

# Periodic disclosures for all companies in range (max ~3 months if corp omitted — API rule)
dart.list(start='2022-01-01', end='2022-03-30', kind='A')

'''
kind: disclosure type
* A : periodic (annual/quarterly reports)
* B : major events
* C : issuance
* D : shareholdings
* E : other
* F : external audit (audit reports)
* G : funds
* H : asset securitization
* I : exchange disclosures
* J : FTC disclosures
'''

# ==== 1-2. Company profile ====
dart.company('005930')
dart.company_by_name('삼성전자')

# ==== 1-3. Original filing document ====
xml_text = dart.document('20220816001711')

# ==== All parts (e.g. business + audit) ====
xml_text_list = dart.document_all('20220816001711')
xml_text = xml_text_list[0]

# ==== 1-4. Corporation code ====
dart.find_corp_code('005930')
dart.find_corp_code('삼성전자')


### 2. Business report sections ###
# Available keywords (Korean), e.g.:
# ['조건부자본증권미상환', '미등기임원보수', '회사채미상환', ... '배당', ... '타법인출자']

dart.report('005930', '미등기임원보수', 2021)
dart.report('005930', '증자', 2021)
dart.report('005930', '배당', 2018)


### 3. Listed-company financials (non-financial sector) ###
dart.finstate('삼성전자', 2021)
dart.finstate('삼성전자', 2021, reprt_code='11013')

dart.finstate('00126380,00164779,00164742', 2021)
dart.finstate('005930, 000660, 005380', 2021)
dart.finstate('삼성전자, SK하이닉스, 현대자동차', 2021)

dart.finstate_xml('20220308000798', save_as='삼성전자_2021_사업보고서_XBRL.zip')

dart.finstate_all('005930', 2021)

dart.xbrl_taxonomy('BS1')


### 4. Shareholding disclosures ###
dart.major_shareholders('삼성전자')
dart.major_shareholders_exec('005930')

### 5. Major-event reports ###
# dart.event(corp, event, start=None, end=None)
# Event names are Korean API literals, e.g.:
# ['부도발생', '영업정지', '회생절차', ... '유상증자', ...]

dart.event('052220', '영업정지', '2019')
dart.event('라이트론', '회생절차', '2019')
dart.event('휴림네트웍스', '유상증자')
dart.event('미원상사', '무상증자')
dart.event('017810', '전환사채발행')
dart.event('키다리스튜디오', '신주인수권부사채발행')
dart.event('이스트소프트', '교환사채발행')


### 6. Registration statements (증권신고서) ###
# dart.regstate(corp, key_word, start=None, end=None)

dart.regstate('하림지주', '주식의포괄적교환이전')
dart.regstate('사조대림', '합병')
dart.regstate('에스앤케이', '증권예탁증권')
dart.regstate('BNK금융지주', '채무증권')
dart.regstate('금호전기', '지분증권')
dart.regstate('케이씨씨', '분할')

### 7. Extensions ###
dart.list_date_ex('2022-10-03')

rcp_no = '20220308000798'
dart.sub_docs(rcp_no)
dart.sub_docs(rcp_no, match='감사의견')

url = 'http://dart.fss.or.kr/pdf/download/excel.do?rcp_no=20220308000798&dcm_no=8446647&lang=ko'
fn = '[삼성전자]사업보고서_재무제표(2022.03.08)_ko.xls'
dart.download(url, fn)

for fname, file_url in dart.attach_files('20221111000817').items():
    dart.download(file_url, fname)

dart.list_presenter('국민연금공단', start='2026-01-01', end='2026-05-01', report_type='지분공시')
```

**2021–2026 [FinanceData.KR](https://financedata.kr)**
