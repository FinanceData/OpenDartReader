def test_simple():
    assert 1 == 1

import OpenDartReader

# API 키 설정 (환경변수에서 자동으로 로드)
dart = OpenDartReader()

# 공시 검색 (삼성전자, 2024년 이후)
df_list = dart.list("삼성전자", start="2024-01-01")
print("\n--- 공시 검색 결과 ---")
print(df_list.head())   