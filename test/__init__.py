import sys
import os
import unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import test_client
import test_collection
import test_sso

if __name__ == '__main__':
    unittest.main()