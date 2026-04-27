"""Unit tests for bmVarargin utilities."""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.varargin.bmVarargin import bmVarargin, bmVarargin_unpack
from src.varargin.bmVarargin_kernelType_nWin_kernelParam import bmVarargin_kernelType_nWin_kernelParam


class TestBmVarargin:
    def test_returns_list(self):
        result = bmVarargin(1, 2, 3)
        assert result == [1, 2, 3]

    def test_empty_args(self):
        result = bmVarargin()
        assert result == []

    def test_single_arg(self):
        result = bmVarargin('hello')
        assert result == ['hello']


class TestBmVararginUnpack:
    def test_pads_with_none(self):
        result = bmVarargin_unpack([1, 2], 4)
        assert result == [1, 2, None, None]

    def test_truncates(self):
        result = bmVarargin_unpack([1, 2, 3, 4, 5], 3)
        assert result == [1, 2, 3]

    def test_empty_list(self):
        result = bmVarargin_unpack([], 3)
        assert result == [None, None, None]

    def test_none_input(self):
        result = bmVarargin_unpack(None, 2)
        assert result == [None, None]


class TestBmVararginKernelType:
    def test_defaults_gauss(self):
        kt, nw, kp = bmVarargin_kernelType_nWin_kernelParam(None, None, None)
        assert kt == 'gauss'
        assert nw == 3.0
        assert len(kp) == 2

    def test_gauss_defaults(self):
        kt, nw, kp = bmVarargin_kernelType_nWin_kernelParam('gauss', None, None)
        assert kt == 'gauss'
        assert nw == 3.0
        np.testing.assert_allclose(kp[0], np.float64(np.float32(0.61)), rtol=1e-6)
        np.testing.assert_allclose(kp[1], np.float64(np.float32(10.0)), rtol=1e-6)

    def test_kaiser_defaults(self):
        kt, nw, kp = bmVarargin_kernelType_nWin_kernelParam('kaiser', None, None)
        assert kt == 'kaiser'
        assert len(kp) == 3

    def test_custom_nwin(self):
        _, nw, _ = bmVarargin_kernelType_nWin_kernelParam(None, 5, None)
        assert nw == pytest.approx(float(np.float64(np.float32(5))), rel=1e-6)

    def test_custom_kernelparam(self):
        _, _, kp = bmVarargin_kernelType_nWin_kernelParam('gauss', None, [0.5, 8])
        assert kp.shape == (2,)
        np.testing.assert_allclose(kp[0], np.float64(np.float32(0.5)), rtol=1e-5)

    def test_wrong_gauss_params_raises(self):
        with pytest.raises(ValueError):
            bmVarargin_kernelType_nWin_kernelParam('gauss', None, [0.5, 5, 10])

    def test_wrong_kaiser_params_raises(self):
        with pytest.raises(ValueError):
            bmVarargin_kernelType_nWin_kernelParam('kaiser', None, [1.95, 10])

    def test_dtype_double(self):
        _, nw, kp = bmVarargin_kernelType_nWin_kernelParam(None, None, None)
        assert isinstance(nw, float)
        assert kp.dtype == np.float64
