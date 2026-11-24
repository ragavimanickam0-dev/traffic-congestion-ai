"""
TrafficIntel AI - Automated Test Runner
Executes Authentication, Machine Learning, and API endpoint integration tests.
"""

import unittest
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.tests.test_auth import TestAuthSecurity
from backend.tests.test_ml import TestMachineLearningService
from backend.tests.test_endpoints import TestAPIEndpoints

def run_all_tests():
    print("=================================================================", flush=True)
    print(" Running TrafficIntel AI Automated Test Suite", flush=True)
    print("=================================================================\n", flush=True)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestAuthSecurity))
    suite.addTests(loader.loadTestsFromTestCase(TestMachineLearningService))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n=================================================================", flush=True)
    if result.wasSuccessful():
        print(f" ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!", flush=True)
        print("=================================================================", flush=True)
        return 0
    else:
        print(f" TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors", flush=True)
        print("=================================================================", flush=True)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
