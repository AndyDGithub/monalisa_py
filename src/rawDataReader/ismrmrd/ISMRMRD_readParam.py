from __future__ import annotations

def ISMRMRD_readParam(argFile, autoFlag):
    """
    function varargout = ISMRMRD_readParam(argFile, autoFlag)
    % varargout = ISMRMRD_readParam(argFile, automaticFlag)
    % 
    % This function extracts the meta data from the ISMRM raw data file. Al
Allows
    % for user modification of the meta data if the flag is set to true. Th
The
    % code execution is interrupted during the modification.
    %
    % Authors:
    %   Dominik Helbing
    %   MattechLab 2024
    %
    % Parameters:
    %   argFile (Char): The path to the file.
    %   autoFlag (Logical): Flag; Does allow user modification if false.
    %   Simplifies use if true.
    %
    % Returns:
    %   varargout{1}: bmMriAcquisitionParam object containing the extracted
extracted
    %   meta data.
    %   varargout{2}: Double containing the extracted reconstruction FoV.
    """
    
    # Import required libraries
    import h5py
    from xml.etree.ElementTree import ElementTree, fromstring
    
    # Read dataset and XML from file
    with h5py.File(argFile, "r") as f:
        raw_data = f['/dataset/data'][:]
        myXML = f['/dataset/xml'][()]
    
    # Parse the XML string using ElementTree
    xml_root = fromstring(myXML.decode())
    
    # Extract acquisition parameters
    myMriAcquisition_node = {}
    nLine = raw_data.shape[0]
    myMriAcquisition_node['nLine'] = nLine
    
    encodedSpace = xml_root.find(".//encodedSpace")
    fovEncoded = encodedSpace.find("fieldOfView_mm")
    xFoV = float(fovEncoded.find("x").text)
    yFoV = float(fovEncoded.find("y").text)
    zFoV = float(fovEncoded.find("z").text)
    myMriAcquisition_node['FoV'] = [xFoV, yFoV, zFoV] * 2
    
    reconSpace = xml_root.find(".//reconSpace")
    fovRecon = reconSpace.find("fieldOfView_mm")
    xFoV_recon = float(fovRecon.find("x").text)
    yFoV_recon = float(fovRecon.find("y").text)
    zFoV_recon = float(fovRecon.find("z").text)
    reconFoV = [xFoV_recon, yFoV_recon, zFoV_recon] * 2
    myMriAcquisition_node['reconFoV'] = reconFoV
    
    # Return the extracted data and FoV
    return myMriAcquisition_node, reconFoV
