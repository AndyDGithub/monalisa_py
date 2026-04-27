from src.arrayUtility.bmPointReshape import bmPointReshape
from src.mathOp.bmMult import bmMult
from src.mathOp.bmSquaredNorm import bmSquaredNorm
from tests.ci.setup_test_path import setup_test_path
import numpy as np

from third_part.matlab_compat.matlab_native import addpath, load


def h(unused):
    thisFile = __file__
    testsDir = os.path.dirname(os.path.abspath(thisFile))  # .../tests
    addpath(os.path.join(testsDir, "ci"))
    setup_test_path()
    return os.getcwd()


def s(testCase):
    dataDir = os.getenv("MONALISA_CI_DATA_DIR")
    repoRoot = os.getenv("MONALISA_REPO_ROOT")
    thisFile = __file__
    testsDir = os.path.dirname(os.path.abspath(thisFile))  # .../tests
    repoRoot = os.path.dirname(testsDir)
    dataDir = os.path.join(repoRoot, "temp", "ci_data")
    p = os.path.join(dataDir, "synthetic_cases.mat")

    s = load(p, "cases")
    testCase.Cases = s["cases"]
    return loadCase


def s(testCase):
    cases = testCase.Cases
    testCase.assertGreater(len(cases), 5)
    metrics = np.zeros((1, len(cases)))
    for i in range(len(cases)):
        c = cases[i]
        x = bmPointReshape(c["raw"], c["nCh"])
        x2 = bmMult(x, np.conj(x))
        e = bmSquaredNorm(x2, c["scalarWeight"])
        metrics[0, i] = e
    testCase.assertTrue(np.all(np.isfinite(metrics)))
    testCase.assertTrue(np.all(metrics >= 0))
    testCase.assertGreater(np.std(metrics), 0)
    return testMiniPipelineOverAllCase


def TestSyntheticDataE2E(unused):
    return h(unused)
