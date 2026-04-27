# matlab/bmFieldPlot3_image.py
"""
bmFieldPlot3_image
------------------

This module contains a lightweight Python implementation of the MATLAB
function `bmFieldPlot3_image`.  It mimics the essential behaviour:
* reshape the input arrays to match the dimensions of ``argImagesTable``
* normalise velocity components
* create a meshgrid of the x/y/z coordinates
* plot the image (using ``imshow``) and overlay a quiver field
* return the resulting matplotlib Figure object

The implementation focuses on correctness and minimalism; all
interactivity (callbacks, figure navigation, multiple frames, etc.)
present in the original MATLAB code is omitted.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple

__all__ = ["bmFieldPlot3_image"]


def _reshape_to_image_shape(arr: np.ndarray, shape: Tuple[int, int, int]) -> np.ndarray:
    """Reshape an array to a 3-D shape defined by the image table."""
    return np.reshape(arr, shape)


def _compute_spacing(coord: np.ndarray) -> float:
    """Return the spacing between the first two points of a 1-D coordinate array.
    Handles the trivial case of a single element by returning 1.0.
    """
    if coord.size > 1:
        return float(np.abs(coord[1] - coord[0]))
    return 1.0


def _create_meshgrid(nx: int, ny: int, nz: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return 3-D meshgrid arrays for the given dimensions."""
    x = np.arange(nx)
    y = np.arange(ny)
    z = np.arange(nz)
    return np.meshgrid(x, y, z, indexing="ij")


def _prepare_quiver_data(
    vx: np.ndarray, vy: np.ndarray, vz: np.ndarray, norm_max: float
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Normalise velocity components and clip to ``norm_max``."""
    # Clip velocities to avoid excessively large arrows
    vx = np.clip(vx, -norm_max, norm_max)
    vy = np.clip(vy, -norm_max, norm_max)
    vz = np.clip(vz, -norm_max, norm_max)
    return vx, vy, vz


def _plot_frame(
    ax: plt.Axes,
    img: np.ndarray,
    quiver_x: np.ndarray,
    quiver_y: np.ndarray,
    quiver_u: np.ndarray,
    quiver_v: np.ndarray,
    auto_scale: bool,
):
    """Draw an image frame and overlay a quiver field on ``ax``."""
    # Image (equivalent to imagesc in MATLAB)
    ax.imshow(img, origin="lower", cmap="gray", aspect="equal")

    # Quiver overlay
    if auto_scale:
        ax.quiver(quiver_x, quiver_y, quiver_u, quiver_v, color="r")
    else:
        ax.quiver(
            quiver_x,
            quiver_y,
            quiver_u,
            quiver_v,
            scale_units="xy",
            scale=1,
            color="r",
        )


def bmFieldPlot3_image(
    arg_x: np.ndarray,
    arg_y: np.ndarray,
    arg_z: np.ndarray,
    arg_vx: np.ndarray,
    arg_vy: np.ndarray,
    arg_vz: np.ndarray,
    autoScaleFlag: bool,
    myNorm_max: float,
    argImagesTable: np.ndarray,
) -> plt.Figure:
    """
    Minimal Python replacement for the MATLAB function
    ``bmFieldPlot3_image``.
    Parameters
    ----------
    arg_x, arg_y, arg_z : array_like
        Coordinates (will be reshaped to match ``argImagesTable``).
    arg_vx, arg_vy, arg_vz : array_like
        Velocity components (same dimensionality as ``argImagesTable``).
    autoScaleFlag : bool
        If ``True`` the quiver field is drawn without explicit scaling.
    myNorm_max : float
        Maximum velocity magnitude used for clipping arrows (only relevant
        when ``autoScaleFlag`` is ``False``).
    argImagesTable : array_like, shape (nx, ny, nz)
        3-D image data to be displayed. ``nz`` can be 1 (single frame) or
        more (multiframe data).
    Returns
    -------
    fig : matplotlib.figure.Figure
        Figure containing the image and quiver plot.
    Notes
    -----
    The implementation is intentionally simple - it does not reproduce the
    full interactivity of the original MATLAB code.  The function is
    designed to run in a headless environment (e.g. unit tests) and
    therefore suppresses ``plt.show()``.
    """
    # Determine target shape (nx, ny, nz)
    target_shape = argImagesTable.shape
    if len(target_shape) < 3:
        raise ValueError("argImagesTable must be at least 3-D")
    nx, ny, nz = target_shape[:3]

    # Reshape all inputs to the image table shape
    arg_x = _reshape_to_image_shape(arg_x, (nx, ny, nz))
    arg_y = _reshape_to_image_shape(arg_y, (nx, ny, nz))
    arg_z = _reshape_to_image_shape(arg_z, (nx, ny, nz))
    arg_vx = _reshape_to_image_shape(arg_vx, (nx, ny, nz))
    arg_vy = _reshape_to_image_shape(arg_vy, (nx, ny, nz))
    arg_vz = _reshape_to_image_shape(arg_vz, (nx, ny, nz))

    # Compute coordinate spacings
    dX = _compute_spacing(arg_x.ravel())
    dY = _compute_spacing(arg_y.ravel())
    dZ = _compute_spacing(arg_z.ravel())

    # Normalise velocity components
    arg_vx = arg_vx / dX
    arg_vy = arg_vy / dY
    arg_vz = arg_vz / dZ

    # Clip velocity magnitudes if scaling is manual
    if not autoScaleFlag:
        arg_vx, arg_vy, arg_vz = _prepare_quiver_data(
            arg_vx, arg_vy, arg_vz, myNorm_max
        )

    # Create meshgrid (for quiver positions)
    grid_x, grid_y, grid_z = _create_meshgrid(nx, ny, nz)

    # Use the first slice (nz=1) for the quiver overlay - this
    # mirrors MATLAB's behaviour when a single frame is visualised.
    # If ``nz`` > 1 the function simply picks the first frame.
    img_slice = argImagesTable[..., 0]  # shape (nx, ny)
    quiver_x = grid_x[..., 0]
    quiver_y = grid_y[..., 0]
    quiver_u = arg_vy[..., 0]  # horizontal component (u)
    quiver_v = arg_vx[..., 0]  # vertical component (v)

    # Create a figure - no interactive display
    fig, ax = plt.subplots(figsize=(6, 6))
    _plot_frame(
        ax,
        img_slice,
        quiver_x,
        quiver_y,
        quiver_u,
        quiver_v,
        autoScaleFlag,
    )

    # Set a clear title and labels - useful for debugging
    ax.set_title("bmFieldPlot3_image")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")

    # The function intentionally **does not** call ``plt.show()``
    # so that it can run in headless environments (e.g. CI pipelines).
    return fig
