"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourier123.map_function.nonCartesian.bmNasha import bmNasha
from src.imDisp.bmImage import bmImage
from src.image123.bmImClose import bmImClose
from src.image123.bmImOpen import bmImOpen
from src.image123.bmImShiftList import bmImShiftList
from src.imageN.bmMIP import bmMIP
from src.imageN.bmRMS import bmRMS
from third_part.matlab_compat.matlab_native import double, legend, num2str, plot, title, xlabel, ylabel

def bmCoilSense_nonCart_mask(y, Gn, varargin):
    # m = bmCoilSense_nonCart_mask(y, Gn, varargin)
    # 
    # This function creates a mask for the regridded data which is calculated
    # with a matrix multiplication of Gn*y. The mask depends on the optional
    # parameters (varargin) that allow to give a threshold value for RMS and
    # MIP (Maximum Intensity Projection), and min and max values for x, y, z.
    # 
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # 
    # Contributors:
    # Dominik Helbing (Documentation & Comments)
    # MattechLab 2024
    # 
    # Parameters:
    # y (array): Raw data that should be gridded onto the grid defined by the
    # bmSparseMat in Gn.
    # Gn (bmSparseMat): Sparse Matrix defining the new uniform grid.
    # varargin{1}: Lower boundary of the x indices of the mask (ROI).
    # varargin{2}: Upper boundary of the x indices of the mask (ROI).
    # varargin{3}: Lower boundary of the y indices of the mask (ROI).
    # varargin{4}: Upper boundary of the y indices of the mask (ROI).
    # varargin{5}: Lower boundary of the z indices of the mask (ROI).
    # varargin{6}: Upper boundary of the z indices of the mask (ROI).
    # varargin{7}: Threshold for RMS value.
    # varargin{8}: Threshold for MIP value.
    # varargin{9}: Value (not yet commented)
    # varargin{10}: Value (not yet commented)
    # varargin{11}: Flag; Display images if true.
    # 
    # Returns:
    # m (array): Mask for grid defined by Gn masking all pixels outside the
    # ROI and below threshold values, by setting their points in the mask to
    # 0
    # 
    # Notes:
    # The x, y, z constrictions are meant to exclude high intensity pixels
    # outside the main image. These could be due to artifacts.
    # This is rerunnable multiple times therefore you can have as inputs
    # the outputs.
    # % Initialize arguments
    # magic number
    colorMax = 100
    # Extract optional arguments
    # TODO(matlab-line): [   x_min, x_max, ...
    y_min, y_max,
    z_min, z_max,
    th_RMS, th_MIP,
    open_size,
    close_size,
    # TODO(matlab-line): display_flag]    = bmVarargin(varargin);
    N_u     = double(Gn.N_u.ravel().T)
    imDim   = np.shape(N_u.ravel(), 1)
    # % Calculate RMS and MIP
    # Grid y onto the uniform grid of size N_u, given in block format and image
    # space
    x       = bmBlockReshape(bmNasha(y, Gn, N_u), N_u)
    # Calculate RMS for each data point across all channel
    myRMS = bmRMS(x, N_u)
    # Perform MIP for each data point
    myMIP = bmMIP(x, N_u)
    # Normalize and scale RMS and MIP values (maybe devide by max - min)
    myRMS = colorMax*(myRMS - min(myRMS.ravel()))/max(myRMS.ravel())
    myMIP = colorMax*(myMIP - min(myMIP.ravel()))/max(myMIP.ravel())
    # Get number of points of x
    nPix = np.shape(myRMS.ravel(), 1)
    n_RMS = np.zeros(1, colorMax)
    n_MIP = np.zeros(1, colorMax)
    # Calculate the fraction of points having a value bigger than every
    # integer from 0 to colorMax-1 (create histogram for threshold decision)
    # TODO(matlab-control): for i = 0:colorMax-1
    # TODO(matlab-line): n_RMS(1, i+1) = sum(myRMS(:) > i)/nPix;
    # TODO(matlab-line): n_MIP(1, i+1) = sum(myMIP(:) > i)/nPix;
    # TODO(matlab-control): if display_flag
    # Create histogram for threshold decision
    figure
    # TODO(matlab-line): hold on
    plot(n_RMS, ".-")
    plot(n_MIP, ".-")
    xlabel("X")
    ylabel("Fraction above X")
    legend("RMS", "MIP")
    title("Fraction of points having a value above X")
    # Create interactive figures to display RMS and MIP values
    bmImage(myRMS)
    title("RMS")
    bmImage(myMIP)
    title("MIP")
    # % Create mask
    # Create mask for valid RMS and MIP values
    # TODO(matlab-line): m = true(size(myRMS));
    # Use threshold to decide lowest valid value
    # Use RMS threshold for both if MIP th is not given
    # TODO(matlab-control): if not(isempty(th_RMS)) & isempty(th_MIP)
    m = (myRMS > th_RMS) & (myMIP > th_RMS)
    # Use MIP threshold for both if RMS th is not given
    # TODO(matlab-control): elseif isempty(th_RMS) & not(isempty(th_MIP))
    m = (myRMS > th_MIP) & (myMIP > th_MIP)
    # TODO(matlab-control): elseif not(isempty(th_RMS)) && not(isempty(th_MIP))
    m = (myRMS > th_RMS) & (myMIP > th_MIP)
    # Modify mask to crop the image in every dimension if max and min values
    # are given
    # TODO(matlab-control): if imDim == 1
    # Crop the image in x direction if max and min values are given
    # TODO(matlab-control): if not(isempty(x_min)) && not(isempty(x_max))
    # TODO(matlab-line): m(1:x_min, 1)   = false;
    # TODO(matlab-line): m(x_max:end, 1) = false;
    # TODO(matlab-control): if imDim == 2
    # Crop the image in x direction if max and min values are given
    # TODO(matlab-control): if not(isempty(x_min)) && not(isempty(x_max))
    # TODO(matlab-line): m(1:x_min, :)   = false;
    # TODO(matlab-line): m(x_max:end, :) = false;
    # Crop the image in y direction if max and min values are given
    # TODO(matlab-control): if not(isempty(y_min)) && not(isempty(y_max))
    # TODO(matlab-line): m(:, 1:y_min)   = false;
    # TODO(matlab-line): m(:, y_max:end) = false;
    # TODO(matlab-control): if imDim == 3
    # Crop the image in x direction if max and min values are given
    # TODO(matlab-control): if not(isempty(x_min)) && not(isempty(x_max))
    # TODO(matlab-control): if x_min > 1
    # TODO(matlab-line): m(1:x_min-1,   :, :)  = false;
    # TODO(matlab-control): if x_max < N_u(1, 1)
    # TODO(matlab-line): m(x_max+1:end, :, :)  = false;
    # Crop the image in y direction if max and min values are given
    # TODO(matlab-control): if not(isempty(y_min)) && not(isempty(y_max))
    # TODO(matlab-control): if y_min > 1
    # TODO(matlab-line): m(:, 1:y_min-1,   :)  = false;
    # TODO(matlab-control): if y_max < N_u(1, 2)
    # TODO(matlab-line): m(:, y_max:end, :)  = false;
    # Crop the image in z direction if max and min values are given
    # TODO(matlab-control): if not(isempty(z_min)) && not(isempty(z_max))
    # TODO(matlab-control): if z_min > 1
    # TODO(matlab-line): m(:, :, 1:z_min)    = false;
    # TODO(matlab-control): if z_max < N_u(1, 3)
    # TODO(matlab-line): m(:, :, z_max:end)  = false;
    # TO BE COMMENTED
    # TODO(matlab-control): if not(isempty(open_size))
    # TODO(matlab-control): if open_size > 0
    m = bmImOpen(m, bmImShiftList(["sphere", num2str(imDim)], open_size, 0))
    # TODO(matlab-control): if not(isempty(close_size))
    # TODO(matlab-control): if close_size > 0
    m = bmImClose(m, bmImShiftList(["sphere", num2str(imDim)], close_size, 0))
    # Show RMS with mask applied next to the mask in an interactive figure
    # TODO(matlab-control): if sum(m(:) == false) > 0
    # TODO(matlab-line): temp_im = m.*myRMS;
    # Combine normalized applied mask RMS and mask
    temp_im = cat(2, temp_im/max(np.abs(temp_im.ravel())), m)
    # TODO(matlab-control): if display_flag
    bmImage(temp_im)
    # Prepare mask for output
    m = bmBlockReshape(m, N_u)
    return m
