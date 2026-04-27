"""
Mitosius Data Preparation Script
Port of mitosius_script.m to Python.

Prepares data for reconstruction by:
1. Loading raw brain scan data, coil sensitivity maps, and binning masks.
2. Computing trajectories, volume elements, and normalizing the data.
3. Applying the selected binning strategy (AllLines or Sequential).

Environment variables
---------------------
MONALISA_MITOSIUS_ROI_MODE
    'interactive' to use roipoly GUI; anything else (or unset) uses
    automatic thresholding.  Default: auto.
MONALISA_MITOSIUS_ROI_THRESH_FRAC
    Fraction of the image maximum used as the threshold for the auto ROI.
    Default: 0.25
MONALISA_MITOSIUS_ROI_CENTER_FRAC
    Fraction of the smallest image dimension used as the half-size of the
    fallback central box when fewer than 1 % of pixels pass the threshold.
    Default: 0.30
MONALISA_MITOSIUS_BINNING
    'alllines' or 'sequential' (case-insensitive).  Default: 'alllines'.
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

from src.arrayUtility.bmMitosis import bmMitosis
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda
from src.geom123.bmVolumeElement import bmVolumeElement
from src.image123.bmImResize import bmImResize
from src.mitosius.bmMitosius_create import bmMitosius_create
from src.rawDataReader.createRawDataReader import createRawDataReader
from src.trajN.bmTraj import bmTraj


def mitosius_script(data_dir=None, results_dir=None):
    """
    Run the Mitosius data preparation pipeline.

    Parameters
    ----------
    data_dir : str, optional
        Path to the data directory.  Defaults to the sibling monalisa
        repository's data folder.
    results_dir : str, optional
        Path where result files are read from / written to.
        Defaults to data_dir/results.
    """
    if data_dir is None:
        data_dir = _data_dir
    if results_dir is None:
        results_dir = os.path.join(data_dir, 'results')

    os.makedirs(results_dir, exist_ok=True)

    # File paths
    brain_scan_file = os.path.join(data_dir, 'brainScan.dat')
    coil_sensitivity_path = os.path.join(results_dir, 'coil_sensitivity_map.mat')
    all_lines_binnings_path = os.path.join(results_dir, 'allLinesBinning.mat')
    seq_binnings_path = os.path.join(results_dir, 'sequentialBinning.mat')

    # ------------------------------------------------------------------
    # Step 1: Load the Raw Data
    # ------------------------------------------------------------------
    reader = createRawDataReader(brain_scan_file, False)
    p = reader.acquisitionParams
    p.traj_type = 'full_radial3_phylotaxis'

    # Load raw data and compute trajectory and volume elements
    y_tot = reader.readRawData(True, True)   # filter nShotOff and SI
    t_tot = bmTraj(p)
    ve_tot = bmVolumeElement(t_tot, 'voronoi_full_radial3')

    # ------------------------------------------------------------------
    # Step 2: Load Coil Sensitivity Maps
    # ------------------------------------------------------------------
    coil_data = scipy.io.loadmat(coil_sensitivity_path)
    C = coil_data['C']

    FoV = p.FoV
    matrix_size = FoV / 3  # Max nominal spatial resolution
    N_u = [matrix_size, matrix_size, matrix_size]
    C = bmImResize(C, [48, 48, 48], N_u)

    # ------------------------------------------------------------------
    # Step 3: Normalize the Raw Data
    # ------------------------------------------------------------------
    x_tot = bmMathilda(y_tot, t_tot, ve_tot, C, N_u, N_u, [1, 1, 1] / 384)

    roi_mode = os.environ.get('MONALISA_MITOSIUS_ROI_MODE', 'auto')

    if roi_mode == 'interactive':
        # Interactive path: requires a display
        from src.imDisp.bmImage import bmImage
        import matplotlib.pyplot as plt
        bmImage(x_tot)
        temp_im = np.abs(x_tot[:, :, x_tot.shape[2] // 2]).astype(np.float32)
        bmImage(temp_im)
        # roipoly equivalent via matplotlib
        from matplotlib.widgets import PolygonSelector
        fig, ax = plt.subplots()
        ax.imshow(temp_im, cmap='gray')
        selected_verts = []

        def onselect(verts):
            selected_verts.extend(verts)

        selector = PolygonSelector(ax, onselect)
        plt.show()
        # Build mask from polygon
        from matplotlib.path import Path as MplPath
        nr, nc = temp_im.shape
        xx, yy = np.meshgrid(np.arange(nc), np.arange(nr))
        coords = np.column_stack([xx.ravel(), yy.ravel()])
        if selected_verts:
            poly_path = MplPath(selected_verts)
            temp_roi = poly_path.contains_points(coords).reshape(nr, nc)
        else:
            temp_roi = np.ones_like(temp_im, dtype=bool)
        normalize_val = float(np.mean(np.abs(temp_im[temp_roi])))
        if normalize_val == 0 or not np.isfinite(normalize_val):
            normalize_val = 1.0
    else:
        # Automatic ROI based on threshold
        # Use magnitude of central slice
        temp_im = np.abs(x_tot[:, :, x_tot.shape[2] // 2]).astype(np.float32)

        roi_thresh_frac = float(os.environ.get('MONALISA_MITOSIUS_ROI_THRESH_FRAC', '0.25'))
        roi_center_frac = float(os.environ.get('MONALISA_MITOSIUS_ROI_CENTER_FRAC', '0.30'))

        mx = np.max(np.abs(temp_im))
        if mx > 0:
            thresh = roi_thresh_frac * mx
            temp_roi = np.abs(temp_im) >= thresh
            if np.sum(temp_roi) < max(1, round(temp_roi.size * 0.01)):
                # Fallback to central box
                nr, nc = temp_im.shape
                half_size = max(1, round(min(nr, nc) * roi_center_frac / 2))
                cr, cc = nr // 2, nc // 2
                temp_roi = np.zeros_like(temp_im, dtype=bool)
                temp_roi[
                    max(0, cr - half_size):min(nr, cr + half_size),
                    max(0, cc - half_size):min(nc, cc + half_size)
                ] = True
        else:
            temp_roi = np.ones_like(temp_im, dtype=bool)

        normalize_val = float(np.mean(np.abs(temp_im[temp_roi])))
        if normalize_val == 0 or not np.isfinite(normalize_val):
            normalize_val = 1.0

    y_tot = y_tot / normalize_val

    # ------------------------------------------------------------------
    # Step 4: Select Binning Strategy
    # ------------------------------------------------------------------
    binning_choice = os.environ.get('MONALISA_MITOSIUS_BINNING', 'alllines').strip().lower()

    if binning_choice == 'sequential':
        binning_path = seq_binnings_path
        save_folder_suffix = 'mitosius_sequential'
        print('Sequential binning selected.')
    else:
        # Default: AllLines
        binning_path = all_lines_binnings_path
        save_folder_suffix = 'mitosius_allLines'
        print('AllLines binning selected.')

    binning_data = scipy.io.loadmat(binning_path)
    mask = binning_data['mask']  # shape: (nBins, nLines)

    # Create the save folder
    save_folder = os.path.join(results_dir, save_folder_suffix)
    os.makedirs(save_folder, exist_ok=True)

    # ------------------------------------------------------------------
    # Reshape and clean the binning mask
    # MATLAB:
    #   mask = reshape(mask, [size(mask,1), p.nSeg, size(mask,2)/p.nSeg]);
    #   mask(:, 1, :) = [];          % Remove SI projection column
    #   mask(:, :, 1:p.nShot_off) = [];  % Remove non-SS shots
    #   mask = bmPointReshape(mask);
    # ------------------------------------------------------------------
    nBins = mask.shape[0]
    nLines = mask.shape[1]
    nSeg = int(p.nSeg)
    nShot_off = int(p.nShot_off)

    # Reshape to (nBins, nSeg, nLines/nSeg)
    mask = mask.reshape(nBins, nSeg, nLines // nSeg)

    # Remove SI projection: column index 0 in the second dimension (MATLAB col 1)
    mask = np.delete(mask, 0, axis=1)

    # Remove non-steady-state shots: first nShot_off slices along the third dim
    mask = mask[:, :, nShot_off:]

    # Flatten back for bmPointReshape
    mask = bmPointReshape(mask)

    # ------------------------------------------------------------------
    # Step 5: Apply Mitosis Function
    # ------------------------------------------------------------------
    y, t = bmMitosis(y_tot, t_tot, mask, n_tables=2)
    y = bmPermuteToCol(y)
    ve = bmVolumeElement(t, 'voronoi_full_radial3')

    # Save the results
    bmMitosius_create(save_folder, y, t, ve)
    print(f'Mitosius preparation complete. Data saved to: {save_folder}')


if __name__ == '__main__':
    mitosius_script()
