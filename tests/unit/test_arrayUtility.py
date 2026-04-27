import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import numpy as np
import pytest
from src.arrayUtility.bmCol import bmCol
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmNumOfDim import bmNumOfDim
from src.arrayUtility.bmIndex2MultiIndex import bmIndex2MultiIndex
from src.arrayUtility.bmMultiIndex2Index import bmMultiIndex2Index
from src.arrayUtility.bmInvPerm import bmInvPerm
from src.arrayUtility.bmIsBlockShape import bmIsBlockShape
from src.arrayUtility.bmIsColShape import bmIsColShape
from src.arrayUtility.bmIsScalar import bmIsScalar
from src.arrayUtility.bmType import bmType
from src.arrayUtility.bmZero import bmZero
from src.arrayUtility.bmOne import bmOne
from src.arrayUtility.bmRand import bmRand
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPermuteToPoint import bmPermuteToPoint
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmFirstIndex import bmFirstIndex
from src.arrayUtility.bmZeroCleaned import bmZeroCleaned

def test_bmCol_2d():
    a = np.array([[1,2],[3,4]])
    out = bmCol(a)
    assert out.size == 4

def test_bmCol_empty():
    assert bmCol(np.array([])).size == 0

def test_bmBlockReshape_basic():
    out = bmBlockReshape(np.arange(24), [2,3,2])
    assert out.shape == (2,3,2,2)

def test_bmBlockReshape_nCh1():
    out = bmBlockReshape(np.arange(24), [2,3,4])
    assert out.shape == (2,3,4,1)

def test_bmBlockReshape_empty():
    assert bmBlockReshape(np.array([]), [2,2,2]).size == 0

def test_bmBlockReshape_incompatible():
    with pytest.raises(Exception):
        bmBlockReshape(np.arange(10), [3,3])

def test_bmNumOfDim_1d():
    assert bmNumOfDim(np.array([1,2,3])) == 1

def test_bmNumOfDim_2d():
    assert bmNumOfDim(np.ones((3,4))) == 2

def test_bmNumOfDim_3d():
    assert bmNumOfDim(np.ones((2,3,4))) == 3

def test_bmNumOfDim_scalar():
    assert bmNumOfDim(np.array(5.0)) == 1

def test_index_roundtrip_2d():
    size = [2, 3]
    for i in range(1, 7):
        mi = bmIndex2MultiIndex(i, size)
        back = bmMultiIndex2Index(mi, size)
        assert back == i

def test_index_roundtrip_3d():
    size = [2, 3, 4]
    for i in range(1, 25):
        assert bmMultiIndex2Index(bmIndex2MultiIndex(i, size), size) == i

def test_index2multi_known():
    assert list(bmIndex2MultiIndex(5, [2,3])) == [1,3]
    assert list(bmIndex2MultiIndex(1, [2,3])) == [1,1]
    assert list(bmIndex2MultiIndex(6, [2,3])) == [2,3]

def test_bmInvPerm_basic():
    perm = np.array([2,0,1])
    inv = bmInvPerm(perm)
    np.testing.assert_array_equal(inv[perm], np.arange(3))

def test_bmInvPerm_identity():
    perm = np.array([0,1,2])
    np.testing.assert_array_equal(bmInvPerm(perm), perm)

def test_bmIsBlockShape_true():
    assert bmIsBlockShape(np.zeros((4,8,4,3)), [4,8,4]) is True

def test_bmIsBlockShape_false():
    assert bmIsBlockShape(np.zeros((4,8,4)), [4,8,4]) is False

def test_bmIsColShape_true():
    assert bmIsColShape(np.zeros((128,3)), [128]) is True

def test_bmIsColShape_false():
    assert bmIsColShape(np.zeros((64,3)), [128]) is False

def test_bmIsScalar():
    assert bmIsScalar(4.0) is True
    assert bmIsScalar(np.array(3)) is True
    assert bmIsScalar([1]) is False
    assert bmIsScalar(np.array([1,2])) is False

def test_bmType():
    assert bmType(np.ones(3, dtype=np.float64)) == "real_double"
    assert bmType(np.ones(3, dtype=np.float32)) == "real_single"
    assert bmType(np.ones(3, dtype=np.complex128)) == "complex_double"
    assert bmType(np.ones(3, dtype=np.complex64)) == "complex_single"

def test_bmZero():
    z = bmZero([3,4], "real_double")
    assert z.shape == (3,4) and z.dtype == np.float64 and np.all(z==0)

def test_bmZero_complex():
    z = bmZero([2,2], "complex_single")
    assert z.dtype == np.complex64

def test_bmOne_complex():
    o = bmOne([2,3], "complex_double")
    assert o.shape == (2,3) and np.all(o == (1+0j))

def test_bmRand_shape():
    r = bmRand([3,4], "real_single")
    assert r.shape == (3,4) and r.dtype == np.float32

def test_bmPermuteToCol_no_size():
    y = np.array([[1,2,3],[4,5,6]], dtype=float)
    out = bmPermuteToCol(y)
    assert out.shape == (3,2)

def test_bmPermuteToCol_with_size():
    # argSize specifies nPt; nCh = total/nPt; out shape = (nPt, nCh)
    y = np.arange(12, dtype=float).reshape(3, 4)
    out = bmPermuteToCol(y, 3)  # nPt=3, nCh=4 -> shape (3,4)
    assert out.shape == (3, 4)

def test_bmPermuteToPoint_roundtrip():
    y = np.arange(12, dtype=float).reshape(3,4)
    col = bmPermuteToCol(y)
    back = bmPermuteToPoint(col, 4)
    np.testing.assert_array_equal(back, y)

def test_bmColReshape_basic():
    out = bmColReshape(np.arange(24, dtype=float), [2,3,4])
    assert out.shape == (24, 1)

def test_bmColReshape_multi_ch():
    out = bmColReshape(np.arange(48, dtype=float), [2,3,4])
    assert out.shape == (24, 2)

def test_bmFirstIndex_equalTo():
    v = np.array([3,1,4,1,5])
    assert bmFirstIndex("equalTo", 1, v) == 1
    assert bmFirstIndex("equalTo", 9, v) == 5

def test_bmFirstIndex_biggerThan():
    v = np.array([1.0,2.0,3.0,4.0])
    assert bmFirstIndex("biggerThan", 2.5, v) == 2

def test_bmZeroCleaned():
    out = bmZeroCleaned(np.array([0,1,0,2,3,0]))
    np.testing.assert_array_equal(out, [1,2,3])
