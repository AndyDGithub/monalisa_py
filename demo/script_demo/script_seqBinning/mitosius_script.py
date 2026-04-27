import numpy as np
from demo.function_demo.function_seqBinning.mleGenerateSequentialBinningMasks import mleGenerateSequentialBinningMasks
from src.arrayUtility.bmMitosis import bmMitosis
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda
from src.geom123.bmVolumeElement import bmVolumeElement
from src.imDisp.bmImage import bmImage
from src.image123.bmImResize import bmImResize
from src.mitosius.bmMitosius_create import bmMitosius_create
from src.rawDataReader.createRawDataReader import createRawDataReader
from third_part.matlab_compat.matlab_native import load


def mitosius_script():
    windowSizeSeconds = 150
    # path where to save mitosius
    mitosius_savepath = r"/Users/mauroleidi/Desktop/20240923_Data/JB/mitosius/"
    savefolder = [mitosius_savepath, str(windowSizeSeconds), "seconds_PSF"]

    # path to the rawdatafile (in this case Siemens raw data)
    f = r"/Users/mauroleidi/Desktop/20240923_Data/JB/Raw_Data/rawdata/meas_MID00485_FID176652_BEAT_LIBREoff_RS_GoldenStep.dat"
    autoFlag = False  # Set whether the validation UI is shown

    # Create the appropriate reader based on the file extension
    reader = createRawDataReader(f, autoFlag)
    p = reader.acquisitionParams
    p.selfNav_flag = True
    p.traj_type = "full_radial3_phylotaxis_chris"
    # compute trajectory points. This function is really weird. ASK BASTIEN.
    y_tot = reader.readRawData(True, True);  # get raw data without nshotoff and SI
    t_tot = bmTraj(p)  # get trajectory without nshotoff and SI

    # compute volume elements
    ve_tot = bmVolumeElement(t_tot, "voronoi_full_radial3")
    FoV = p.FoV
    matrix_size = FoV / 3
    N_u = [matrix_size, matrix_size, matrix_size]
    n_u = [matrix_size, matrix_size, matrix_size]

    # TODO(matlab-line): dK_u    = [1, 1, 1]./384;
    # Load the coil sensitivity previously measured
    load(r"/Users/mauroleidi/Desktop/20240923_Data/JB/coil_sensitivity_map_2024-09-28_21-13.mat")
    C = bmImResize(C, [48, 48, 48], N_u)

    # Normalization (probably to converge better)
    # Note you can normalize the rawdata and the image will be normalized
    # This is because the Fourier transform is linear
    # F(f(.)/a) =  F(f(.))/a
    x_tot = bmMathilda(y_tot, t_tot, ve_tot, C, N_u, n_u, dK_u=None)
    bmImage(x_tot)
    temp_im = getimage(gca)
    bmImage(temp_im)
    temp_roi = roipoly
    normalize_val = np.mean(temp_im(temp_roi.ravel()))
    # only once !!!!
    y_tot = y_tot / normalize_val
    nshotoff = p.nShot_off

    # Compute binning
    cMask = mleGenerateSequentialBinningMasks(windowSizeSeconds, reader, True)
    print(np.shape(cMask))
    cMask = np.reshape(cMask, [np.shape(cMask)[1], p.nSeg, np.shape(cMask)[2] // p.nSeg])  # MAGIC NUMBERS

    # TODO(matlab-line): cMask[:, 1, :] = [];  % remove the SI projection
    # TODO(matlab-line): cMask[:, :, 1:p.nShot_off] = []; % remove non steady state
    print(np.shape(cMask))

    # TODO(matlab-control): if size(cMask, 0) > 10
    # TODO(matlab-line): cMask = cMask(1:10, :, :);  % Keep only the first 10 images
    cMask = bmPointReshape(cMask)

    # Run the mitosis function and compute volume elements
    [y, t] = bmMitosis(y_tot, t_tot, cMask)
    y = bmPermuteToCol(y)
    ve = bmVolumeElement(t, "voronoi_full_radial3")
    # Save all the resulting datastructures on the disk. You are now ready
    # to run your reconstruction
    bmMitosius_create(savefolder, y, t, ve)
