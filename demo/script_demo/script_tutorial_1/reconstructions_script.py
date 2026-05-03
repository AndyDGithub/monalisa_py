"""
Reconstructions Script
Port of reconstructions_script.m to Python.

Uses data prepared by mitosius_script to run:
- Mathilda (regridded) reconstruction
- Sensa (iterative SENSE) reconstruction
- bmTevaMorphosia_chain (compressed sensing) reconstruction
"""

import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_monalisa_py_root = os.path.abspath(os.path.join(_script_dir, '..', '..', '..', '..'))
if _monalisa_py_root not in sys.path:
    sys.path.insert(0, _monalisa_py_root)

_monalisa_root = os.path.abspath(os.path.join(_monalisa_py_root, '..', 'monalisa'))
_data_dir = os.path.join(_monalisa_root, 'demo', 'data_demo', 'data_8_tutorial_1')
_results_dir = os.path.join(_data_dir, 'results')

import numpy as np
import scipy.io

from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda
from src.fourier123.solver_function.imDim.nonCartesian.bmSensa import bmSensa
from src.fourier123.solver_function.imDim_morphosia.nonCartesian.bmTevaMorphosia_chain import bmTevaMorphosia_chain
from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
from src.image123.bmImResize import bmImResize
from src.mitosius.bmMitosius_load import bmMitosius_load
from src.optim.bmWitnessInfo import bmWitnessInfo
from src.rawDataReader.createRawDataReader import createRawDataReader


def reconstructions_script(data_dir=None, results_dir=None):
    """
    Run all reconstruction methods on the prepared mitosius data.

    Parameters
    ----------
    data_dir : str, optional
        Path to the data directory.  Defaults to the sibling monalisa
        repository's data folder.
    results_dir : str, optional
        Path to the results directory.  Defaults to data_dir/results.
    """
    if data_dir is None:
        data_dir = _data_dir
    if results_dir is None:
        results_dir = os.path.join(data_dir, 'results')

    # File paths
    brain_scan_file = os.path.join(data_dir, 'brainScan.dat')
    coil_sensitivity_path = os.path.join(results_dir, 'coil_sensitivity_map.mat')
    all_lines_binnings_path = os.path.join(results_dir, 'mitosius_allLines')
    seq_binnings_path = os.path.join(results_dir, 'mitosius_sequential')

    # Load mitosius allLines data
    y = bmMitosius_load(all_lines_binnings_path, 'y')
    t = bmMitosius_load(all_lines_binnings_path, 't')
    ve = bmMitosius_load(all_lines_binnings_path, 've')

    reader = createRawDataReader(brain_scan_file, False)
    p = reader.acquisitionParams

    FoV = p.FoV
    matrix_size = FoV / 3
    N_u = [matrix_size, matrix_size, matrix_size]
    n_u = N_u
    dK_u = np.array([1.0, 1.0, 1.0]) / FoV

    # Load coil sensitivity
    coil_data = scipy.io.loadmat(coil_sensitivity_path)
    C = coil_data['C']
    C = bmImResize(C, [48, 48, 48], N_u)

    # ------------------------------------------------------------------
    # Regridded reconstruction: Mathilda (allLines, frame 0)
    # MATLAB: x0 = bmMathilda(y{1}, t{1}, ve{1}, ...)   [1-indexed]
    # Python:                  y[0], t[0], ve[0]         [0-indexed]
    # ------------------------------------------------------------------
    x0 = bmMathilda(y[0], t[0], ve[0], C, N_u, n_u, dK_u, [], [], [], [])

    # ------------------------------------------------------------------
    # Sequential data: Mathilda for each frame
    # ------------------------------------------------------------------
    y = bmMitosius_load(seq_binnings_path, 'y')
    t = bmMitosius_load(seq_binnings_path, 't')
    ve = bmMitosius_load(seq_binnings_path, 've')

    # MATLAB: nFr = size(y, 1)  - y is a cell array, size along dim 1
    # Python: y is a list, so len(y)
    nFr = len(y)
    # Limit to 8 frames to speed things up
    nFr = min(8, nFr)

    x1 = [None] * nFr
    for i in range(nFr):
        x1[i] = bmMathilda(y[i], t[i], ve[i], C, N_u, n_u, dK_u, [], [], [], [])

    # ------------------------------------------------------------------
    # Iterative SENSE reconstruction: Sensa
    # bmTraj2SparseMat returns (Gu, Gut) - two outputs, not three
    # ------------------------------------------------------------------
    Gu, Gut = bmTraj2SparseMat(t, ve, N_u, dK_u)

    nIter = 30
    witness_ind = list(range(0, nIter, 3))  # equivalent to MATLAB 1:3:nIter (0-indexed)
    nCGD = 4
    ve_max = 10 * float(np.prod(dK_u))

    x_sensa = [None] * nFr
    for i in range(nFr):
        witnessInfo = bmWitnessInfo(f'sensa_frame_{i}', witness_ind)
        x_sensa[i] = bmSensa(
            x1[i], y[i], ve[i], C, Gu[i], Gut[i], n_u, nCGD, ve_max, nIter, witnessInfo
        )

    # ------------------------------------------------------------------
    # Compressed Sensing reconstruction: bmTevaMorphosia_chain
    # ------------------------------------------------------------------
    Gu, Gut = bmTraj2SparseMat(t, ve, N_u, dK_u)

    nIter = 30
    delta = 0.1
    rho = 10 * delta
    witness_ind = list(range(0, nIter, 3))
    nCGD = 4

    x_cs = bmTevaMorphosia_chain(
        x1,
        [], [],
        y[:nFr], ve[:nFr], C,
        Gu, Gut, n_u,
        [], [],
        delta, rho, 'normal',
        nCGD, ve_max,
        nIter,
        bmWitnessInfo('tevaMorphosia_d0p1_r1_nCGD4', witness_ind)
    )

    return x0, x1, x_sensa, x_cs


if __name__ == '__main__':
    reconstructions_script()
