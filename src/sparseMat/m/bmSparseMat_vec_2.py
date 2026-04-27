"""MATLAB to Python port of ``bmSparseMat_vec_2.m``.

This function dispatches to mex-style sparse operators depending on:
- row/column vector layout
- real/complex input
- one-block/multi-block sparse structure
- optional OpenMP backend
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _matlab_error(message: str) -> None:
    raise RuntimeError(message)


def _matlab_class(value: Any) -> str:
    if value is None:
        return "NoneType"
    return value.__class__.__name__


def _as_varargin(varargin: Any) -> tuple[Any, ...]:
    if varargin is None:
        return tuple()
    if isinstance(varargin, tuple):
        return varargin
    if isinstance(varargin, list):
        return tuple(varargin)
    return (varargin,)


def _size_dim(value: np.ndarray, dim: int) -> int:
    if dim < 1:
        raise ValueError("MATLAB dimensions are 1-based.")
    if value.ndim < dim:
        return 1
    return int(value.shape[dim - 1])


def _mex_missing(name: str):
    def _missing(*_args, **_kwargs):
        raise NotImplementedError(f"{name} wrapper not provided.")

    return _missing


bmSparseMat_rR_oBlock_mex = _mex_missing("bmSparseMat_rR_oBlock_mex")
bmSparseMat_rR_nBlock_mex_omp = _mex_missing("bmSparseMat_rR_nBlock_mex_omp")
bmSparseMat_cR_oBlock_2_mex = _mex_missing("bmSparseMat_cR_oBlock_2_mex")
bmSparseMat_cR_nBlock_2_mex_omp = _mex_missing("bmSparseMat_cR_nBlock_2_mex_omp")
bmSparseMat_rC_oBlock_mex_omp = _mex_missing("bmSparseMat_rC_oBlock_mex_omp")
bmSparseMat_rC_oBlock_mex = _mex_missing("bmSparseMat_rC_oBlock_mex")
bmSparseMat_cC_oBlock_2_mex_omp = _mex_missing("bmSparseMat_cC_oBlock_2_mex_omp")
bmSparseMat_cC_oBlock_2_mex = _mex_missing("bmSparseMat_cC_oBlock_2_mex")


def bmSparseMat_vec_2(s: Any, v: Any, varargin: Any = None) -> Any:
    """Port of ``bmSparseMat_vec_2`` with MATLAB-compatible branching."""
    v_arr = np.asarray(v)
    if v_arr.ndim > 2:
        _matlab_error("The input list of vectors 'v' is a matrix that cannot have more that 2 dim. ")

    s_class = _matlab_class(s)
    v_class = "single" if v_arr.dtype in (np.float32, np.complex64) else "double" if v_arr.dtype in (
        np.float64,
        np.complex128,
    ) else str(v_arr.dtype)

    if s_class == "bmSparseMat":
        if v_class != "single":
            _matlab_error("The class bmSparseMat is for single class only. ")
    else:
        if v_class != "double":
            _matlab_error("Matlab sparse matrices are implemented for double class only. ")

    # MATLAB fallback for native sparse/double matrix multiplication.
    if s_class != "bmSparseMat" and v_class == "double":
        return s * v_arr

    args = _as_varargin(varargin)
    omp_flag = False
    if args:
        first = args[0]
        if first == "omp":
            omp_flag = True
        elif isinstance(first, (bool, np.bool_)):
            omp_flag = bool(first)

    l_squeeze_flag = not (getattr(s, "l_jump", None) is None or len(np.atleast_1d(getattr(s, "l_jump", []))) == 0)

    v_shape = np.asarray(v_arr.shape, dtype=np.int64).reshape(-1)
    if v_shape.size == 1:
        v_shape = np.array([v_shape[0], 1], dtype=np.int64)

    if int(v_shape[0]) >= int(v_shape[1]):
        n_vec_32 = np.int32(_size_dim(v_arr, 2))
        t_flag = False
    else:
        n_vec_32 = np.int32(_size_dim(v_arr, 1))
        t_flag = True

    r_flag = not np.iscomplexobj(v_arr)

    block_type = str(getattr(s, "block_type", ""))
    if block_type == "one_block":
        one_block_flag = True
    elif block_type == "multi_block":
        one_block_flag = False
    else:
        _matlab_error("The bmSparseMat is not cpp_prepared. ")

    if t_flag:
        if r_flag:
            if one_block_flag:
                return bmSparseMat_rR_oBlock_mex(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    v_arr,
                    n_vec_32,
                )
            if omp_flag:
                return bmSparseMat_rR_nBlock_mex_omp(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    s.nBlock,
                    s.block_length,
                    s.l_block_start,
                    s.m_block_start,
                    v_arr,
                    n_vec_32,
                )
            _matlab_error("Case not implemented. ")
        else:
            if one_block_flag:
                return bmSparseMat_cR_oBlock_2_mex(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    v_arr,
                    n_vec_32,
                )
            if omp_flag:
                return bmSparseMat_cR_nBlock_2_mex_omp(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    s.nBlock,
                    s.block_length,
                    s.l_block_start,
                    s.m_block_start,
                    v_arr,
                    n_vec_32,
                )
            _matlab_error("Case not implemented")
    else:
        if r_flag:
            if one_block_flag:
                if omp_flag:
                    return bmSparseMat_rC_oBlock_mex_omp(
                        s.r_size,
                        s.r_jump,
                        s.r_nJump,
                        s.m_val,
                        s.l_size,
                        s.l_jump,
                        s.l_nJump,
                        l_squeeze_flag,
                        v_arr,
                        n_vec_32,
                    )
                return bmSparseMat_rC_oBlock_mex(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    v_arr,
                    n_vec_32,
                )
            _matlab_error("Case not implemented")
        else:
            if one_block_flag:
                if omp_flag:
                    return bmSparseMat_cC_oBlock_2_mex_omp(
                        s.r_size,
                        s.r_jump,
                        s.r_nJump,
                        s.m_val,
                        s.l_size,
                        s.l_jump,
                        s.l_nJump,
                        l_squeeze_flag,
                        v_arr,
                        n_vec_32,
                    )
                return bmSparseMat_cC_oBlock_2_mex(
                    s.r_size,
                    s.r_jump,
                    s.r_nJump,
                    s.m_val,
                    s.l_size,
                    s.l_jump,
                    s.l_nJump,
                    l_squeeze_flag,
                    v_arr,
                    n_vec_32,
                )
            _matlab_error("Case not implemented")

    _matlab_error("Unexpected control flow in bmSparseMat_vec_2.")
