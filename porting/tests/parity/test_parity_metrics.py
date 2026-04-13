import numpy as np
import pytest

from monalisa_py.parity import compare_image_parity, l2_loss, nmse


def test_l2_and_nmse_zero_when_equal():
    x = np.array([[1.0, 2.0], [3.0, 4.0]])
    assert l2_loss(x, x) == 0.0
    assert nmse(x, x) == 0.0


def test_l2_and_nmse_detector_small_difference():
    a = np.ones((4, 4))
    b = a + 1e-4
    m = compare_image_parity(a, b, l2_threshold=1e-8, nmse_threshold=1e-8)
    assert m.l2_loss > 0
    assert m.nmse > 0
    assert not m.ok_l2
    assert not m.ok_nmse


def test_compare_image_parity_thresholds():
    a = np.zeros((5, 5))
    b = np.zeros((5, 5))
    result = compare_image_parity(a, b, l2_threshold=1e-6, nmse_threshold=1e-6)
    assert result.ok_l2
    assert result.ok_nmse


def test_shape_mismatch_raises_value_error():
    a = np.zeros((2, 2))
    b = np.zeros((3, 3))
    with pytest.raises(ValueError):
        l2_loss(a, b)
    with pytest.raises(ValueError):
        nmse(a, b)


def test_load_generated_matlab_parity_image_if_available():
    from pathlib import Path
    from monalisa_py.parity import load_matlab_image, compare_image_parity

    root = Path(__file__).resolve().parents[4]  # monalisa_py/porting -> PA-Monalisa workspace root
    mat_file = root / 'monalisa' / 'temp' / 'ci_data' / 'matlab_parity_image.mat'

    if not mat_file.exists():
        pytest.skip('MATLAB parity .mat file not generated yet')

    try:
        matlab_img = load_matlab_image(mat_file)
    except RuntimeError as exc:
        if "scipy is required" in str(exc):
            pytest.skip("scipy not installed, skipping .mat parity loading test")
        raise
    python_img = np.array(matlab_img, dtype=np.float64)
    r = compare_image_parity(matlab_img, python_img)
    assert r.ok_l2
    assert r.ok_nmse
