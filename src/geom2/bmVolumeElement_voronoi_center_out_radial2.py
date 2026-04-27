from src.traj123.bmTraj_norm import bmTraj_norm
def bmVolumeElement_voronoi_center_out_radial2(t):
    # format trajectory
    t, _, formatedIndex, formatedWeight = bmTraj_formatTraj(t)
    imDim = t.shape[0]
    if imDim != 2:
        raise ValueError("The trajectory must be 2Dim.")
    centerFlag = False
    if np.linalg.norm(t[:,0]) < 100*np.finfo(t.dtype).eps:
        centerFlag = True
        t = t[:,1:,:]  # remove center line
    t = bmTraj_lineReshape(t)
    imDim = t.shape[0]
    N = t.shape[1]
    nLine = t.shape[2]
    e = bmTraj_lineDirection(t)
    dr = np.zeros((N, nLine))
    for i in range(nLine):
        dr[:,i] = t[:,:,i].T @ e[:,i]
    dr = bmVolumeElement1(dr)
    # r1, r2
    r_1 = np.zeros((1,1,nLine))
    for i in range(imDim):
        r_1 += t[i,0,:]**2
    r_1 = np.sqrt(r_1).reshape(-1)
    r_2 = np.zeros((1,1,nLine))
    for i in range(imDim):
        r_2 += t[i,1,:]**2
    r_2 = np.sqrt(r_2).reshape(-1)
    if centerFlag:
        dr[0,:] = r_2/2
    else:
        dr[0,:] = (r_1 + r_2)/2
    # ds
    myAngle = np.angle(e[0,:] + 1j*e[1,:])
    sorted_angle = np.sort(myAngle)
    myPerm = np.argsort(myAngle)
    myInvPerm = np.argsort(myPerm)
    myAngle = sorted_angle
    myCutSpace = (np.pi - myAngle[-1]) + (myAngle[0] - (-np.pi))
    myVoronoi_1 = (myAngle[1] - myAngle[0])/2 + myCutSpace/2
    myVoronoi_end = (myAngle[-1] - myAngle[-2])/2 + myCutSpace/2
    myAngleVoronoi = bmVoronoi(myAngle)
    myAngleVoronoi[0] = myVoronoi_1
    myAngleVoronoi[-1] = myVoronoi_end
    myAngleVoronoi = myAngleVoronoi[myInvPerm]
    myAngleVoronoi = np.tile(myAngleVoronoi, (N,1))
    ds = bmTraj_norm(t) * myAngleVoronoi
    v = (dr.reshape(-1)*ds.reshape(-1))
    if centerFlag:
        dr_0 = np.mean(r_1/2)
        v0 = np.pi*(dr_0**2)
        v = np.concatenate(([v0], v))
    v = v.reshape(-1)
    # adjust weights
    v = v[formatedIndex]*formatedWeight
    return v
