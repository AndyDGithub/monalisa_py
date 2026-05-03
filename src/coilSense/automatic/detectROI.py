from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def _imbinarize(data: np.ndarray) -> np.ndarray:
    """Return a binary array where values > th are True."""
    return data > graythresh(data)

def detectROI(rawData, N_u):
    """
    Detect a region of interest in a 3D image by Otsu thresholding and
    extracting the largest connected component.

    Parameters
    ----------
    rawData : array_like
        3-D image data.
    N_u : array_like
        Expected size of each dimension.

    Returns
    -------
    bBox : ndarray
        Array of shape (3, 2) containing minimum coordinate and width
        for each dimension: [xMin, xWidth; yMin, yWidth; zMin, zWidth].
    """
    # Increase box in all directions by this value (magic number)
    padding = 3

    # Ensure correct size
    N_u = np.asarray(N_u).ravel()
    rawData = bmBlockReshape(rawData, N_u)

    # Sum over every dimension and normalize
    zData = np.sum(rawData, axis=2)
    zData = (zData - zData.min()) / (zData.max() - zData.min())

    yData = np.transpose(rawData, (2, 0, 1))
    yData = np.sum(yData, axis=2)
    yData = (yData - yData.min()) / (yData.max() - yData.min())

    xData = np.transpose(rawData, (1, 2, 0))
    xData = np.sum(xData, axis=2)
    xData = (xData - xData.min()) / (xData.max() - xData.min())

    # Combine data in 4th dimension to use a loop
    nData = np.stack((xData, yData, zData), axis=-1)

    # Create bounding box around biggest connected component
    boxes = np.zeros((3, 2))

    for i in range(3):
        data = nData[..., i]
        binary = _imbinarize(data)
        cc = label(binary, connectivity=1)
        stats = regionprops(cc)
        idx = int(np.argmax([s.area for s in stats]))
        bbox = stats[idx].bbox  # (min_row, min_col, max_row, max_col)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        boxes[i, 0] = bbox[1]  # min_col -> x
        boxes[i, 1] = bbox[0]  # min_row -> y

    # Get minimum and width for each coordinate (position)
    xMin = min(boxes[1, 0], boxes[2, 1])
    yMin = min(boxes[0, 1], boxes[1, 0])
    zMin = min(boxes[0, 0], boxes[1, 1])
    xW = max(boxes[1, 1] - boxes[1, 0], boxes[2, 3] - boxes[2, 0])
    yW = max(boxes[0, 3] - boxes[0, 1], boxes[3, 2] - boxes[3, 0])
    zW = max(boxes[0, 2] - boxes[0, 0], boxes[4, 3] - boxes[4, 0])

    # Add padding, drop decimals and clip the value
    xMin = np.max(np.fix(xMin - padding), 1)
    yMin = np.max(np.fix(yMin - padding), 1)
    zMin = np.max(np.fix(zMin - padding), 1)
    xW = np.min(np.fix(xW + 2 * padding), N_u[0] - xMin)
    yW = np.min(np.fix(yW + 2 * padding), N_u[1] - yMin)
    zW = np.min(np.fix(zW + 2 * padding), N_u[2] - zMin)

    bBox = np.array([[xMin, xW], [yMin, yW], [zMin, zW]])
    return bBox
