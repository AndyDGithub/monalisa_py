from tests.ci.setup_test_path import setup_test_path
import os
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # IMPORT this function

from third_part.matlab_compat.matlab_native import addpath


def h(unused):
    thisFile = __file__
    testsDir = os.path.dirname(os.path.dirname(thisFile))  # .../tests
    addpath(os.path.join(testsDir, "ci"))
    setup_test_path()
    return 'addProjectPath'


def e(testCase):
    repoRoot = os.getenv("MONALISA_REPO_ROOT")
    thisFile = __file__
    testsDir = os.path.dirname(os.path.dirname(thisFile))  # .../tests
    repoRoot = os.path.dirname(testsDir)
    srcRoot = os.path.join(repoRoot, "src")
    files = [f for f in os.listdir(os.path.join(srcRoot, "**"), recursive=True) if f.endswith(".py")]
    testCase.assertGreater(len(files), 0, "No Python source files found.")
    missing = []
    # TODO(matlab-control): for k in range(len(files)):
    # TODO(matlab-line): fn = os.path.splitext(os.path.basename(files[k]))[0]
    # TODO(matlab-control): if not os.path.exists(fn):
    # TODO(matlab-line): missing.append(os.path.join(srcRoot, files[k]))
    testCase.assertListEqual(missing, [], "Some functions are not resolvable on MATLAB path:")


def TestFunctionInventoryUnit(unused):
    return h(unused)
