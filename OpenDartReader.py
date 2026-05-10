from opendartreader.dart import OpenDartReader
import sys

# For backward compatibility with 'import OpenDartReader'
# This allows 'dart = OpenDartReader(api_key)' after 'import OpenDartReader'
sys.modules[__name__] = OpenDartReader
