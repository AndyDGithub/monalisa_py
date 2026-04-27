import numpy as np
from src.arrayUtility.bmMitosis import bmMitosis
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.fourier123.map_function.nonCartesian.bmMathilda import bmMathilda
from src.geom123.bmVolumeElement import bmVolumeElement
from src.imDisp.bmImage import bmImage
from src.image123.bmImResize import bmImResize
from src.mitosius.bmMitosius_create import bmMitosius_create
from src.rawDataReader.createRawDataReader import createRawDataReader
import scipy.io as sio


def mitosius_script():
    # % Paths - Replace for your own case
    # Path to the rawdatafile (Siemens raw data or ISMRMRD)
    filePath = r"C:\Users\andym\hesso\PA-Monalisa\monalisa_py\demo\dataset\1_Pilot_MREye_Data\Sub001\230928_anatomical_MREYE_study\MR_EYE_Subj01\RawData\meas_MID00453_FID57919_BEAT_LIBREon_eye.dat"
    # Previously generated coil sensitivity and binmasks
    CMatPath = r"C:\Users\andym\hesso\PA-Monalisa\monalisa_py\demo\dataset\241017_T1\Sub001\T1_LIBRE_Binning\C\C.mat"
    MaskPath = r"C:\Users\andym\hesso\PA-Monalisa\monalisa_py\demo\dataset\241017_T1\Sub001\T1_LIBRE_Binning\other\eMask_th0.75.mat"
    # Mitosius save path
    mitosiusPath = r"C:\Users\andym\hesso\PA-Monalisa\monalisa_py\demo\dataset\241017_T1\Sub001\T1_LIBRE_Binning\mitosius"
    f = filePath

    # These functions use a function not written by Bastien so they are outside the repo
    import sys
    sys.path.append(r"..\..\\..\\..\\twix_for_monalisa\\")
    autoFlag = False;  # Set whether the validation UI is shown

    # Create the appropriate reader based on the file extension
    reader = createRawDataReader(f, autoFlag)
    p = reader.acquisitionParams
    p.selfNav_flag = True
    p.traj_type = "full_radial3_phylotaxis"
    # Initialize and fill in the parameters: This in theory can be automated;
    p.raw_N_u         = [480, 480, 480]
    # TODO(matlab-line): p.raw_dK_u        = [1, 1, 1]./480;

    # % Read raw data
    y_tot = reader.readRawData(True, True)  # get raw data without nshotoff and SI
    # compute trajectory points
    t_tot = bmTraj(p)  # get trajectory without nshotoff and SI
    # compute volume elements
    ve_tot = bmVolumeElement(t_tot, "voronoi_full_radial3" )
    FoV = p.FoV
    matrix_size = 80
    N_u     = [matrix_size, matrix_size, matrix_size]
    n_u     = [matrix_size, matrix_size, matrix_size]
    # TODO(matlab-line): dK_u    = [1, 1, 1]./FoV;

    # Load the coil sensitivity previously measured
    MaskDict = sio.loadmat(CMatPath)
    C = MaskDict['C']
    C = bmImResize(C, [48, 48, 48], N_u)
    # Normalization (probably to convege better)
    # Note you can normalize the rawdata and the image will be normalized
    # This is because the Fourier transform is linear
    # F(f(.)/a) =  F(f(.))/a
    x_tot = bmMathilda(y_tot, t_tot, ve_tot, C, N_u, n_u)
    bmImage(x_tot)
    temp_im = getimage(gca)
    bmImage(temp_im)
    temp_roi = roipoly
    normalize_val = np.mean(temp_im(temp_roi.ravel()))

    # % only once !!!!
    y_tot = y_tot/normalize_val

    # %
    # Load the binning mask
    MaskDict = sio.loadmat(MaskPath)
    Mask = MaskDict['Mask']
    # Get the bin number and remove non steady state and SI
    nMasks = np.shape(Mask,1)
    Mask = np.reshape(Mask, [nMasks, p.nSeg, p.nShot])
    # TODO(matlab-line): Mask(:, 1, :) = [];
    # TODO(matlab-line): Mask(:, :, 1:p.nShot_off) = [];
    Mask = bmPointReshape(Mask)

    # Run the mitosis function and compute volume elements
    [y, t] = bmMitosis(y_tot, t_tot, Mask)
    y = bmPermuteToCol(y)
    ve  = bmVolumeElement(t, "voronoi_full_radial3" )
    # Save all the resulting datastructures on the disk. You are now ready
    # to run your reconstruction
    m = mitosiusPath
    bmMitosius_create(m, y, t, ve)
