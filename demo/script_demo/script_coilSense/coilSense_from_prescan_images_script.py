from src.arrayUtility import bmBlockReshape
from src.coilSense.from_prescan.bmCoilSense_prescan_coilSense import bmCoilSense_prescan_coilSense
from src.coilSense.from_prescan.bmCoilSense_prescan_mask import bmCoilSense_prescan_mask
import numpy as np


def coilSense_from_prescan_images_script():
    # % param initial
    n_u             = [64, 128]
    display_flag    = True
    # % mask
    x_min           = []
    x_max           = []
    y_min           = []
    y_max           = []
    z_min           = []
    z_max           = []
    th_RMS          = 19
    th_MIP          = 17
    close_size      = []
    open_size       = []

    m = bmCoilSense_prescan_mask(n_u, x_min, x_max, y_min, y_max, z_min, z_max, th_RMS, th_MIP, close_size, open_size, display_flag)
    C   = bmCoilSense_prescan_coilSense(prescan_body, prescan_surface, m, n_u)
