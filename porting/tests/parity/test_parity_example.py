import numpy as np

from monalisa_py.parity import compare_arrays


def test_compare_arrays_exact():
    a = np.array([1.0, 2.0, 3.0])
    b = np.array([1.0, 2.0, 3.0])
    result = compare_arrays(a, b, rtol=1e-12, atol=1e-12)
    assert result.ok
    assert result.max_abs == 0.0
