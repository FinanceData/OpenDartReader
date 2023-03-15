#-*- coding:utf-8 -*-
# 2020-2023 FinanceData.KR http://financedata.kr fb.com/financedata
import sys
from .dart import *

__version__ = '0.2.2'
__all__ = ['__version__', 'OpenDartReader']

sys.modules['OpenDartReader'] = dart.OpenDartReader
