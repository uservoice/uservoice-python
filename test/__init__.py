from __future__ import absolute_import
import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from . import test_client
from . import test_collection
from . import test_sso

if __name__ == '__main__':
    unittest.main()