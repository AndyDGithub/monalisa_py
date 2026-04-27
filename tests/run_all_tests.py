from tests.ci.prepare_ci_data import prepare_ci_data
from tests.ci.setup_test_path import setup_test_path
import unittest
import numpy as np
from third_part.matlab_compat.matlab_native import addpath, disp, fullfile

def run_all_tests():
    suite = unittest.TestSuite()

    # Adding test suites for unit, integration and end-to-end tests
    suite.addTest(unittest.defaultTestLoader.loadTestsFromDir(fullfile(setup_test_path('..', 'tests', 'unit')))
                    .loadTestsFromNames(filter(lambda x: not x.startswith('_'), dir(unittest.TestLoader().discover(fullfile(setup_test_path('..', 'tests', 'unit')), pattern='*.py')))))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromDir(fullfile(setup_test_path('..', 'tests', 'integration')))
                    .loadTestsFromNames(filter(lambda x: not x.startswith('_'), dir(unittest.TestLoader().discover(fullfile(setup_test_path('..', 'tests', 'integration')), pattern='*.py')))))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromDir(fullfile(setup_test_path('..', 'tests', 'e2e')))
                    .loadTestsFromNames(filter(lambda x: not x.startswith('_'), dir(unittest.TestLoader().discover(fullfile(setup_test_path('..', 'tests', 'e2e')), pattern='*.py')))))

    runner = unittest.TextTestRunner()
    results = runner.run(suite)
    print(results)

    if any([result.wasSuccessful() == False for result in results]):
        raise Exception("One or more tests failed.")
