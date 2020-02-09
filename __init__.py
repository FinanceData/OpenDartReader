import sys
from .dart import *

__version__ = '0.0.1'
__all__ = ['__version__', 'OpenDartReader']

sys.modules['OpenDartReader'] = dart.OpenDartReader
