"""
Coil Sensitivity Estimation Script
Port of coilSensitivityEstimation_script.m to Python.

Estimates coil sensitivity maps from body coil and surface coil data, then
saves the result to coil_sensitivity_map.mat.
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

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.coilSense.nonCart.bmCoilSense_nonCart_data import bmCoilSense_nonCart_data
from src.coilSense.nonCart.bmCoilSense_nonCart_mask_automatic import bmCoilSense_nonCart_mask_automatic
from src.coilSense.nonCart.bmCoilSense_nonCart_primary import bmCoilSense_nonCart_primary
from src.coilSense.nonCart.bmCoilSense_nonCart_ref import bmCoilSense_nonCart_ref
from src.coilSense.nonCart.bmCoilSense_nonCart_secondary import bmCoilSense_nonCart_secondary
from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
from src.rawDataReader.createRawDataReader import createRawDataReader


def coilSensitivityEstimation_script(data_dir=None, results_dir=None):
    """
    Estimate coil sensitivity maps and save them to results_dir.

    Parameters
    ----------
    data_dir : str, optional
        Path to the data directory containing bodyCoil.dat and
        surfaceCoil.dat.  Defaults to the sibling monalisa repository's
        data folder.
    results_dir : str, optional
        Path where coil_sensitivity_map.mat will be written.
        Defaults to data_dir/results.
    """
    if data_dir is None:
        data_dir = _data_dir
    if results_dir is None:
        results_dir = os.path.join(data_dir, 'results')

    os.makedirs(results_dir, exist_ok=True)

    body_coil_file = os.path.join(data_dir, 'bodyCoil.dat')
    head_coil_file = os.path.join(data_dir, 'surfaceCoil.dat')

    # Check that the data was downloaded
    if not os.path.exists(body_coil_file):
        raise FileNotFoundError(
            f"The file '{body_coil_file}' was not found.\n"
            "Please follow the instructions in:\n"
            "/monalisa/demo/data_demo/data_8_tutorial_1/README.txt\n"
            "to download the required data."
        )

    # ------------------------------------------------------------------
    # Load and Configure Data
    # ------------------------------------------------------------------
    body_coil_reader = createRawDataReader(body_coil_file, False)
    head_coil_reader = createRawDataReader(head_coil_file, False)

    # Ensure consistency in number of shot-off points
    nShotOff = max(
        body_coil_reader.acquisitionParams.nShot_off,
        head_coil_reader.acquisitionParams.nShot_off,
    )
    body_coil_reader.acquisitionParams.nShot_off = nShotOff
    head_coil_reader.acquisitionParams.nShot_off = nShotOff

    # Select the right trajectory type
    body_coil_reader.acquisitionParams.traj_type = 'full_radial3_phylotaxis'
    head_coil_reader.acquisitionParams.traj_type = 'full_radial3_phylotaxis'

    # ------------------------------------------------------------------
    # Parameters
    # ------------------------------------------------------------------
    dK_u = np.ones(3) / head_coil_reader.acquisitionParams.FoV
    N_u = np.array([48, 48, 48])

    # ------------------------------------------------------------------
    # Compute Trajectory and Volume Elements
    # bmCoilSense_nonCart_data returns (y, t, ve) for body coil and
    # only y for the surface coil (single output variant).
    # ------------------------------------------------------------------
    y_body, t, ve = bmCoilSense_nonCart_data(body_coil_reader, N_u)
    y_surface = bmCoilSense_nonCart_data(head_coil_reader, N_u)

    # ------------------------------------------------------------------
    # Compute the gridding matrices
    # Gn: uniform → non-uniform
    # Gu: non-uniform → uniform
    # Gut: Gu transposed
    # ------------------------------------------------------------------
    Gn, Gu, Gut = bmTraj2SparseMat(t, ve, N_u, dK_u)

    # ------------------------------------------------------------------
    # Create Mask
    # Pass y_body directly (already shaped by bmCoilSense_nonCart_data)
    # ------------------------------------------------------------------
    mask = bmCoilSense_nonCart_mask_automatic(y_body, Gn, False)

    # ------------------------------------------------------------------
    # Reference coil sensitivity (body coil)
    # ------------------------------------------------------------------
    y_ref, C_ref = bmCoilSense_nonCart_ref(y_body, Gn, mask, [])

    # ------------------------------------------------------------------
    # Head coil sensitivity estimate using body coil reference
    # ------------------------------------------------------------------
    C_array_prime = bmCoilSense_nonCart_primary(y_surface, y_ref, C_ref, Gn, ve, mask)

    # ------------------------------------------------------------------
    # Refine with optimisation
    # ------------------------------------------------------------------
    nIter = 5
    C, x = bmCoilSense_nonCart_secondary(
        y_surface, C_array_prime, y_ref, C_ref, Gn, Gu, Gut, ve, nIter, False
    )

    # ------------------------------------------------------------------
    # Save Results
    # ------------------------------------------------------------------
    save_name = os.path.join(results_dir, 'coil_sensitivity_map.mat')
    scipy.io.savemat(save_name, {'C': C})
    print(f'Coil sensitivity map saved to: {save_name}')
    print('You can now go to the binning script')

    return C


if __name__ == '__main__':
    coilSensitivityEstimation_script()
