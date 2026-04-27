from __future__ import annotations
from third_part.matlab_compat.matlab_native import double, movstd, permute, repmat, size, str2double


def dhIsmrmrdReadMetaData(obj):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # varargout = dhIsmrmrdReadMetaData(obj)
    # 
    # This function extracts the meta data from the ISMRM raw data file. Allows
    # for user modification of the meta data if the flag is set to true. The
    # code execution is interrupted during the modification.
    # 
    # Authors:
    # Dominik Helbing
    # adapted by: Mauro Leidi
    # MattechLab 2024
    # 
    # Parameters:
    # obj (mleIsmrmrdReader) the reader object to handle ismrmrd files.
    # 
    # Returns:
    # varargout{1}: bmMriAcquisitionParam object containing the extracted
    # meta data.
    # varargout{2}: Double containing the extracted reconstruction FoV.
    # Extract data and xml
    # Read struct containing the data
    # Read string containting the xml (for FOV)
    # Parse the XML string using parseString
    # Extract acquisition parameters
    # Node for trajectory
    # parse timestamp
    # Number of samples per channel and acquisition
    # Number of acquisitions
    # Number of shots
    # Number of segments per shot
    # Number of channels
    # Number of echos (DON'T KNOW IF THIS WORKS AS I DON'T HAVE ANY DATA
    # CONTAINING MORE THAN ONE ECHO)
    # Throw error if acquisition parameters change during acquisition
    # Extract FOV assuming possible changes in the XML format
    # Get FoV from encoded space
    # Multiply by two as a convention
    # Get FoV from reconstruction space
    # Calculate shot drop off
    # Initialize y
    # Transform it into array
    # Change structure to [nCh, N, nLine]
    # Seperate nLine into nSeg and nShot (nSeg = nLine / nShot)
    # Reduce the array to a 3D array, only containing the values for the first
    # segment
    # Calculate the inverse discret Fourier transform
    # Calculate the RMS along the first dimension (Coils)
    # -> magnitude spectrum of the signal
    # Normalize the magnitude
    # Create 2D array of size N x nShot with each column being [1; 2; ...; N]
    # Calculate the weighted arithmetic mean and the weighted mean (COM)
    # Estimate shotOff (how many shots to be dropped)
    # Define the size of the sliding window
    # Compute the running standard deviation
    # Define a threshold for the std to consider steady state
    # Find the shot where the standard deviation falls below the threshold
    # Set flags in myMriAcquisition_node (Maybe other way to handle them?)
    # Allow manual changes before returning
    # Plot figures and ask for confirmation of the values if should work
    # manualy
    # Return values if required
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: argFile = obj.argFile;
    # MATLAB: autoFlag = obj.autoFlag;
    # MATLAB: myData = h5read(argFile, '/dataset/data');
    # MATLAB: raw_data = myData.data;
    # MATLAB: h = myData.head;
    # MATLAB: myXML = h5read(argFile, '/dataset/xml');
    # MATLAB: import matlab.io.xml.dom.*
    # MATLAB: xmlDoc = parseString(Parser,myXML);
    # MATLAB: myMriAcquisition_node = bmMriAcquisitionParam([]);
    # MATLAB: myMriAcquisition_node.timestamp = h.acquisition_time_stamp;
    # MATLAB: N = double(unique(h.number_of_samples));
    # MATLAB: myMriAcquisition_node.N = N;
    # MATLAB: nLine = size(raw_data(:), 1);
    # MATLAB: myMriAcquisition_node.nLine = nLine;
    # MATLAB: nShot = size(unique(h.idx.segment(:)), 1);
    # MATLAB: myMriAcquisition_node.nShot = nShot;
    # MATLAB: nSeg = nLine / nShot;
    # MATLAB: myMriAcquisition_node.nSeg = nSeg;
    # MATLAB: nCh = double(unique(h.active_channels));
    # MATLAB: myMriAcquisition_node.nCh = nCh;
    # MATLAB: myMriAcquisition_node.nEcho = size(unique(h.idx.contrast(:)), 1);
    # MATLAB: if size(myMriAcquisition_node.N(:), 1) > 1
    # MATLAB: error('Different acquisitions have a different number of samples');
    # MATLAB: end
    # MATLAB: if size(myMriAcquisition_node.nCh(:), 1) > 1
    # MATLAB: error('Different acquisitions have different active channels');
    # MATLAB: end
    # MATLAB: encodedSpace = xmlDoc.getElementsByTagName('encodedSpace').item(0);
    # MATLAB: fovEncoded = encodedSpace.getElementsByTagName('fieldOfView_mm').item(0);
    # MATLAB: reconSpace = xmlDoc.getElementsByTagName('reconSpace').item(0);
    # MATLAB: fovRecon = reconSpace.getElementsByTagName('fieldOfView_mm').item(0);
    # MATLAB: xFoV = str2double(fovEncoded.getElementsByTagName('x').item(0).getTextContent());
    # MATLAB: yFoV = str2double(fovEncoded.getElementsByTagName('y').item(0).getTextContent());
    # MATLAB: zFoV = str2double(fovEncoded.getElementsByTagName('z').item(0).getTextContent());
    # MATLAB: myMriAcquisition_node.FoV = [xFoV, yFoV, zFoV] .* 2;
    # MATLAB: xFoV_recon = str2double(fovRecon.getElementsByTagName('x').item(0).getTextContent());
    # MATLAB: yFoV_recon = str2double(fovRecon.getElementsByTagName('y').item(0).getTextContent());
    # MATLAB: zFoV_recon = str2double(fovRecon.getElementsByTagName('z').item(0).getTextContent());
    # MATLAB: reconFoV = [xFoV_recon, yFoV_recon, zFoV_recon] .* 2;
    # MATLAB: y_raw = complex(zeros([N, nCh, nLine]));
    # MATLAB: for i = 1:nLine
    # MATLAB: acq = raw_data{i};
    # MATLAB: acq = reshape(acq, [2, N, nCh]); % [complex, N, nCh]
    # MATLAB: y_raw(:,:,i) = squeeze(acq(1,:,:) + 1i * acq(2,:,:));
    # MATLAB: end
    # MATLAB: y_raw = permute(y_raw, [2, 1, 3]);
    # MATLAB: y_raw      = reshape(y_raw, [nCh, N, nSeg, nShot]);
    # MATLAB: mySI = squeeze(y_raw(:, :, 1, :));
    # MATLAB: mySI = bmIDF(mySI, 1, [], 2);
    # MATLAB: mySI = squeeze(  sqrt(sum(abs(mySI).^2, 1))  );
    # MATLAB: mySI = mySI - min(mySI(:));
    # MATLAB: mySI = mySI/max(mySI(:));
    # MATLAB: mySize_1 = size(mySI, 1);
    # MATLAB: mySize_2 = size(mySI, 2);
    # MATLAB: x_SI = 1:mySize_1;
    # MATLAB: x_SI = repmat(x_SI(:), [1, mySize_2]);
    # MATLAB: s_mean = mean(x_SI.*mySI, 1);
    # MATLAB: s_center_mass = sum(x_SI.*mySI, 1)./sum(mySI, 1);
    # MATLAB: window_size = 5; %magic number
    # MATLAB: running_std = movstd(s_mean, window_size, 'Endpoints', 'discard');
    # MATLAB: threshold = prctile(running_std, 15);  % 10th percentile of std
    # MATLAB: myMriAcquisition_node.nShot_off = find(running_std < threshold, 1);
    # MATLAB: myMriAcquisition_node.selfNav_flag = true;
    # MATLAB: myMriAcquisition_node.roosk_flag = false;
    # MATLAB: if ~autoFlag
    # MATLAB: [myMriAcquisition_node, reconFoV] = checkMetadataInteractive(mySI, s_mean, ...
    # MATLAB: s_center_mass, myMriAcquisition_node, reconFoV);
    # MATLAB: end
    # MATLAB: if nargout > 0
    # MATLAB: varargout{1} = myMriAcquisition_node;
    # MATLAB: end
    # MATLAB: if nargout > 1
    # MATLAB: varargout{2} = reconFoV;
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    varargout = None
    return varargout
