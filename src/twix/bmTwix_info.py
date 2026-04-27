"""Auto-generated from MATLAB source. Review manually before production use."""

import numpy as np

from src.fourierN.bmIDF import bmIDF

from third_part.matlab_compat.matlab_native import movstd

from src.rawDataReader.ismrmrd.dhIsmrmrdReadMetaData import find
from third_part.matlab_compat.matlab_native import figure, imagesc, legend, permute, plot, repmat, xlabel, xline, ylabel
from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa

def bmTwix_info(myArg):
    # bmTwix_info(myArg)
    # 
    # Prints information included in the Siemens' raw data
    # file's Twix object used in the reconstruction process of the image.
    # 
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # 
    # Parameters:
    # myArg (struct/char): Either the path to the Siemens' raw data file or
    # a Twix object
    # TODO(matlab-control): if isa(myArg, 'char')
    # Read the twix object if path is given
    myTwix = mapVBVD_JH_for_monalisa(myArg)
    # TODO(matlab-control): if iscell(myTwix)
    myTwix = myTwix[end]
    # TODO(matlab-control): else
    myTwix = myArg
    N       = []
    nShot   = []
    nLine   = []
    nSeg    = []
    nPar    = []
    nCh     = []
    nEcho   = []
    hdr_Meas_ReadFoV        = []
    hdr_Meas_FOV            = []
    hdr_Config_ReadFoV      = []
    hdr_Config_PhaseFoV     = []
    hdr_Config_PeFOV        = []
    hdr_Config_RoFOV        = []
    hdr_Dicom_dPhaseFOV     = []
    hdr_Dicom_dReadoutFOV   = []
    hdr_Protocol_ReadFoV    = []
    hdr_Protocol_PeFOV      = []
    hdr_Protocol_PhaseFoV   = []
    # % header
    N           = myTwix.image.NCol
    nShot       = myTwix.image.NSeg
    nLine       = myTwix.image.NLin
    nSeg        = nLine/nShot
    nPar        = myTwix.image.NPar
    nEcho       = myTwix.image.NEco
    # TODO(matlab-control): if isfield(myTwix.hdr, 'Meas')
    # TODO(matlab-control): if isfield(myTwix.hdr.Meas, 'ReadFoV')
    hdr_Meas_ReadFoV = myTwix.hdr.Meas.ReadFoV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Meas, 'FOV')
    hdr_Meas_FOV = myTwix.hdr.Meas.FOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr, 'Config')
    # TODO(matlab-control): if isfield(myTwix.hdr.Config, 'ReadFoV')
    hdr_Config_ReadFoV      = myTwix.hdr.Config.ReadFoV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Config, 'PhaseFoV')
    hdr_Config_PhaseFoV     = myTwix.hdr.Config.PhaseFoV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Config, 'PeFOV')
    hdr_Config_PeFOV        = myTwix.hdr.Config.PeFOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Config, 'RoFOV')
    hdr_Config_RoFOV        = myTwix.hdr.Config.RoFOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr, 'Dicom')
    # TODO(matlab-control): if isfield(myTwix.hdr.Dicom, 'dPhaseFOV')
    hdr_Dicom_dPhaseFOV     = myTwix.hdr.Dicom.dPhaseFOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Dicom, 'dReadoutFOV')
    hdr_Dicom_dReadoutFOV   = myTwix.hdr.Dicom.dReadoutFOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr, 'Protocol')
    # TODO(matlab-control): if isfield(myTwix.hdr.Protocol, 'ReadFoV')
    hdr_Protocol_ReadFoV    = myTwix.hdr.Protocol.ReadFoV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Protocol, 'PeFOV')
    hdr_Protocol_PeFOV   = myTwix.hdr.Protocol.PeFOV*2
    # TODO(matlab-control): if isfield(myTwix.hdr.Protocol, 'PhaseFoV')
    hdr_Protocol_PhaseFoV   = myTwix.hdr.Protocol.PhaseFoV*2
    # % data
    # unsorted() returns the unsorted data as an array [N, nCh, nLine]
    y_raw = myTwix.image.unsorted()
    # Change structure to [nCh, N, nLine]
    y_raw = permute(y_raw, [2, 1, 3])
    # Get nCh
    y_raw_size = np.shape(y_raw)
    y_raw_size = y_raw_size.ravel().T
    nCh        = y_raw_size(1, 1)
    # Seperate nLine into nSeg and nShot (nSeg = nLine / nShot)
    y_raw      = np.reshape(y_raw, [nCh, N, nSeg, nShot])
    # Reduce the array to a 3D array, only containing the values for the first segment
    # TODO(matlab-line): mySI = squeeze(y_raw(:, :, 1, :));
    # Calculate the inverse discret Fourier transform
    mySI = bmIDF(mySI, 1, [], 2)
    # Calculate the RMS along the first dimension (Coils)
    # -> magnitude spectrum of the signal
    # TODO(matlab-line): mySI = squeeze(  sqrt(sum(abs(mySI).^2, 1))  );
    # Normalize the magnitude
    mySI = mySI - min(mySI.ravel())
    mySI = mySI/max(mySI.ravel())
    # Create 2D array of size N x nShot with each column being [1; 2; ...; N]
    mySize_1 = np.shape(mySI, 1)
    mySize_2 = np.shape(mySI, 2)
    # TODO(matlab-line): x_SI = 1:mySize_1;
    x_SI = repmat(x_SI.ravel(), [1, mySize_2])
    # Calculate the weighted arithmetic mean and the weighted mean (COM)
    # TODO(matlab-line): s_mean = mean(x_SI.*mySI, 1);
    # TODO(matlab-line): s_center_mass = sum(x_SI.*mySI, 1)./sum(mySI, 1);
    # Estimate shotOff (how many shots to be dropped)
    window_size = 10;  # Define the size of the sliding window
    threshold = std(s_mean)*0.1;  # 0.01 % Define a threshold for the std to consider steady state
    # Compute the running standard deviation
    running_std = movstd(s_mean, window_size)
    # Find the shot where the standard deviation falls below the threshold
    shotOff = find(running_std < threshold, 1)
    # % Display information
    # Print values
    fprintf("\\n")
    # TODO(matlab-control): if isempty(N)
    fprintf("N     is empty. \\n")
    # TODO(matlab-control): else
    fprintf("N     = %d \\n", N)
    # TODO(matlab-control): if isempty(nSeg)
    fprintf("nSeg  is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nSeg  = %d \\n", nSeg)
    # TODO(matlab-control): if isempty(nShot)
    fprintf("nShot is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nShot = %d \\n", nShot)
    # TODO(matlab-control): if isempty(nLine)
    fprintf("nLine is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nLine = %d \\n", nLine)
    # TODO(matlab-control): if isempty(nPar)
    fprintf("nPar  is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nPar  = %d \\n", nPar)
    # TODO(matlab-control): if isempty(nCh)
    fprintf("nCh   is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nCh   = %d \\n", nCh)
    # TODO(matlab-control): if isempty(nEcho)
    fprintf("nEcho is empty. \\n")
    # TODO(matlab-control): else
    fprintf("nEcho = %d \\n", nEcho)
    fprintf("\\n")
    # Print FoV (Meas)
    # TODO(matlab-control): if isempty(hdr_Meas_ReadFoV)
    fprintf("hdr_Meas_ReadFoV       is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Meas_ReadFoV       = %4.2f \\n", hdr_Meas_ReadFoV)
    # TODO(matlab-control): if isempty(hdr_Meas_FOV)
    fprintf("hdr_Meas_FOV           is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Meas_FOV           = %4.2f \\n", hdr_Meas_FOV)
    fprintf("\\n")
    # Print FoV (Config)
    # TODO(matlab-control): if isempty(hdr_Config_ReadFoV)
    fprintf("hdr_Config_ReadFoV       is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Config_ReadFoV     = %4.2f \\n", hdr_Config_ReadFoV)
    # TODO(matlab-control): if isempty(hdr_Config_PhaseFoV)
    fprintf("hdr_Config_PhaseFoV      is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Config_PhaseFoV    = %4.2f \\n", hdr_Config_PhaseFoV)
    # TODO(matlab-control): if isempty(hdr_Config_PeFOV)
    fprintf("hdr_Config_PeFOV         is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Config_PeFOV       = %4.2f \\n", hdr_Config_PeFOV)
    # TODO(matlab-control): if isempty(hdr_Config_RoFOV)
    fprintf("hdr_Config_RoFOV         is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Config_RoFOV       = %4.2f \\n", hdr_Config_RoFOV)
    fprintf("\\n")
    # Print FoV (Dicom)
    # TODO(matlab-control): if isempty(hdr_Dicom_dPhaseFOV)
    fprintf("hdr_Dicom_dPhaseFOV      is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Dicom_dPhaseFOV    = %4.2f \\n", hdr_Dicom_dPhaseFOV)
    # TODO(matlab-control): if isempty(hdr_Dicom_dReadoutFOV)
    fprintf("hdr_Dicom_dReadoutFOV    is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Dicom_dReadoutFOV  = %4.2f \\n", hdr_Dicom_dReadoutFOV)
    fprintf("\\n")
    # Print FoV (Protocol)
    # TODO(matlab-control): if isempty(hdr_Protocol_ReadFoV)
    fprintf("hdr_Protocol_ReadFoV   is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Protocol_ReadFoV   = %4.2f \\n", hdr_Protocol_ReadFoV)
    # TODO(matlab-control): if isempty(hdr_Protocol_PeFOV)
    fprintf("hdr_Protocol_PeFOV     is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Protocol_PeFOV     = %4.2f \\n", hdr_Protocol_PeFOV)
    # TODO(matlab-control): if isempty(hdr_Protocol_PhaseFoV)
    fprintf("hdr_Protocol_PhaseFoV  is empty. \\n")
    # TODO(matlab-control): else
    fprintf("hdr_Protocol_PhaseFoV  = %4.2f \\n", hdr_Protocol_PhaseFoV)
    fprintf("\\n")
    # Print shotOff value if found
    # TODO(matlab-control): if ~isempty(shotOff)
    fprintf("Steady state reached at shot %d\\n", shotOff)
    # TODO(matlab-control): else
    fprintf("Steady state not reached within the data range.\\n")
    fprintf("\\n")
    # Plotting heatmap of magnitude for the first segment of each shot
    figure("Name", "TwixInfo Magnitude")
    imagesc(mySI, [0, 3*np.mean(mySI.ravel())])
    set(gca,"YDir","normal")
    colorbar
    # TODO(matlab-line): colormap gray
    # Plotting the mean and COM of each shot
    # TODO(matlab-line): hold on
    plot(s_center_mass, "g.-")
    plot(s_mean, "r.-")
    # Plotting vertical line for shotOff
    # TODO(matlab-control): if ~isempty(shotOff)
    xline(shotOff, "c--");  # Add vertical line at steady state index
    # TODO(matlab-line): text(shotOff+5, floor(N*0.75), sprintf('shot = %i', ...
    # TODO(matlab-line): shotOff), "HorizontalAlignment", "left", ...
    # TODO(matlab-line): 'Color', 'black', 'BackgroundColor', 'white', 'Margin', 0.5);
    # Adding legend, title and labels
    legend("Center of Mass", "Mean", "Steady State", "Location", "best")
    xlabel("nShot")
    ylabel("N","Rotation",0)
    # TODO(matlab-line): title(sprintf(['Magnitude spectrum for first segment of each shot\n(estimates ' ...
    # TODO(matlab-line): 'which shots should be excluded)']))
