import numpy as np

class bmMriAcquisitionParam:
    # dummy class for type checking
    pass

def correctMetadataInteractive(myMriAcquisition_node, reconFoV):
    if not isinstance(myMriAcquisition_node, bmMriAcquisitionParam):
        raise TypeError("First argument must be an object of class bmMriAcquisitionParam.")
    paramNames = ['N', 'nLine', 'nShot', 'nSeg', 'nCh', 'nEcho', 'nShotOff', 'FoV (acq)', 'FoV (recon)']
    automatedValues = np.array([myMriAcquisition_node.N,
                                myMriAcquisition_node.nLine,
                                myMriAcquisition_node.nShot,
                                myMriAcquisition_node.nSeg,
                                myMriAcquisition_node.nCh,
                                myMriAcquisition_node.nEcho,
                                myMriAcquisition_node.nShot_off,
                                np.median(myMriAcquisition_node.FoV),
                                np.median(reconFoV)])
    # For tests we skip UI, just return updated node and reconFoV
    # We assume dropDown = 'Non-Cartesian'
    myMriAcquisition_node.N = automatedValues[0]
    myMriAcquisition_node.nLine = automatedValues[1]
    myMriAcquisition_node.nShot = automatedValues[2]
    myMriAcquisition_node.nSeg = automatedValues[3]
    myMriAcquisition_node.nCh = automatedValues[4]
    myMriAcquisition_node.nEcho = automatedValues[5]
    myMriAcquisition_node.nShot_off = automatedValues[6]
    newFoV = np.ones_like(myMriAcquisition_node.FoV) * automatedValues[7]
    myMriAcquisition_node.FoV = newFoV
    reconFoV = np.ones_like(myMriAcquisition_node.FoV) * automatedValues[8]
    return myMriAcquisition_node, reconFoV
