def bmTraj_formatTraj(argTraj, argData=None):
    # Determine shape
    nRows, nCols = argTraj.shape
    # trivial case if nCols < 2
    if nCols < 2:
        formatedTraj = argTraj
        # formatedData: if argData provided, else None
        formatedData = argData
        # formatedIndex: identity mapping from row indices: 1:nRows
        formatedIndex = np.arange(1, nRows+1)
        # formatedWeight: zeros of shape (nRows,1)
        formatedWeight = np.zeros((nRows,1))
        return formatedTraj, formatedData, formatedIndex, formatedWeight
    # compute distance matrix
    distance = np.zeros((nRows, nRows))
    for i in range(nRows):
        for j in range(i, nRows):
            distance[i,j] = np.linalg.norm(argTraj[i,:] - argTraj[j,:])
            distance[j,i] = distance[i,j]
    # compute sorted indices: argmin of distance across each row
    sorted_indices = np.argmin(distance, axis=1)  # zero-based
    # compute distance between sorted indices
    # For each row, find distance to next row's sorted index (sorted_indices[i+1])?
    # In original code, they compute:
    # formatedIndex = zeros(nRows,1);
    # for i=2:nRows
    #    formatedIndex(i) = distance(sorted_indices(i-1), sorted_indices(i));
    # end
    # formatedIndex = [sorted_indices(1); formatedIndex];
    # So formatedIndex[0] = sorted_indices[0]
    # formatedIndex[i] = distance[sorted_indices[i-1], sorted_indices[i]]
    # That mixes integer index with distance values. But this might be expected.

    # But maybe they wanted to produce index sequence of sorted indices and distances. But we'll replicate.

    formatedIndex = np.zeros(nRows, dtype=int)
    for i in range(1, nRows):
        formatedIndex[i] = distance[sorted_indices[i-1], sorted_indices[i]]
    formatedIndex[0] = sorted_indices[0]  # zero-based? In MATLAB, indices start at 1; so adjust accordingly.
