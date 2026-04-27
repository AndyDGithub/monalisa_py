import numpy as np
from src.gridding123.m.bmTraj2SparseMat import bmTraj2SparseMat
from src.coilSense.nonCart.bmCoilSense_nonCart_mask_automatic import bmCoilSense_nonCart_mask_automatic
from src.coilSense.nonCart.bmCoilSense_nonCart_primary import bmCoilSense_nonCart_primary
from src.imDisp.bmImage import bmImage
from src.coilSense.nonCart.bmCoilSense_nonCart_data import bmCoilSense_nonCart_data
from src.coilSense.nonCart.bmCoilSense_nonCart_ref import bmCoilSense_nonCart_ref
from src.coilSense.nonCart.bmCoilSense_nonCart_secondary import bmCoilSense_nonCart_secondary
from src.rawDataReader.createRawDataReader import createRawDataReader
import datetime

from src.elastix.bmTransformix import fileparts


def coilSense_from_prescan_rawdata_nonCart_ISMRMRD_script():
    # This script creates a coil sensitivity map for non cartesian data.
    # SET YOUR PARAMETERS FOR THE COIL SENSITIVITY ESTIMATION
    # K-space resolution for the reconstruction (has to be the same as the
    # final reconstruction)
    reconFoV = 384
    dK_u = [1, 1, 1] / reconFoV

    # Matrix size of the cartesian grid in the k-space
    N_u = np.array([48, 48, 48])
    # END: SET YOUR PARAMETERS

    # % Setup paths and flags
    autoFlag = False
    doSave = True
    bodyCoilFile = []
    arrayCoilFile = []
    saveFolder = []

    pathOutside = fileparts(fileparts(fileparts(fileparts(mfilename("fullpath")))))

    if not bodyCoilFile:
        bodyCoilFile, _ = createRawDataReader(bodyCoilFile, autoFlag)
        bodyCoilFile.acquisitionParams.traj_type = "full_radial3_phylotaxis"
        bodyCoilFile.acquisitionParams.selfNav_flag = True

    if not arrayCoilFile:
        arrayCoilFile, _ = createRawDataReader(arrayCoilFile, autoFlag)
        arrayCoilFile.acquisitionParams.traj_type = "full_radial3_phylotaxis"
        arrayCoilFile.acquisitionParams.selfNav_flag = True

    nShotOff = max(bodyCoilFile.acquisitionParams.nShot_off, arrayCoilFile.acquisitionParams.nShot_off)
    bodyCoilFile.acquisitionParams.nShot_off = nShotOff
    arrayCoilFile.acquisitionParams.nShot_off = nShotOff

    # % Read data and calculate trajectory and volume elements
    y_body, t, ve = bmCoilSense_nonCart_data(bodyCoilFile, N_u)
    y_array, _, _ = bmCoilSense_nonCart_data(arrayCoilFile, N_u)

    print(np.shape(t))
    print(np.shape(y_body))
    print(np.shape(y_array))

    [Gn, Gu, Gut] = bmTraj2SparseMat(t, ve, N_u, dK_u)

    m = bmCoilSense_nonCart_mask_automatic(y_body, Gn, autoFlag)

    # Select one body coil as reference coil and compute its sensitivity
    y_ref, C_ref = bmCoilSense_nonCart_ref(y_body, Gn, m, [])

    # Estimate the coil sensitivity of each surface coil using one body coil
    # image as reference image C_c = (X_c./x_ref)
    C_array_prime = bmCoilSense_nonCart_primary(y_array, y_ref, C_ref, Gn, ve, m)

    nIter = 5
    [C, _] = bmCoilSense_nonCart_secondary(y_array, C_array_prime, y_ref, C_ref, Gn, Gu, Gut, ve, nIter, ~autoFlag)

    # Show the result
    bmImage(C)

    # % Save data
    if doSave:
        currentDateTime = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        saveName = ["coil_sensitivity_map_", currentDateTime, ".mat"]
        savePath = f"{saveFolder}/{saveName[0]}"

        np.save(savePath, C)
