# -------------------------------------------------------------------------
#  bmFieldPlot2_image (Python version)
# -------------------------------------------------------------------------
#  This routine reproduces the core of the MATLAB function
#  bmFieldPlot2_image(arg_x, arg_y, arg_vx, arg_vy, autoScaleFlag,
#                     myNorm_max, argImage).
#
#  Author : Bastien Milani, CHUV/UNIL, Lausanne, Switzerland, 2023
#
#  The MATLAB implementation contains many interactive callbacks that are
#  hard to emulate in a static Python script.  This version focuses on the
#  visualisation part and the essential preprocessing of the field.
#
#  Parameters
#  ----------
#  arg_x, arg_y : array-like, shape (H, W)
#      Spatial coordinates (can be any shape that can be reshaped to the
#      image shape; they are ignored later, because we generate a 1-based
#      grid that matches the image dimensions).
#
#  arg_vx, arg_vy : array-like, shape (H, W)
#      Vector field components.  They are normalised by the grid spacing
#      in X and Y (as the MATLAB code does).
#
#  autoScaleFlag : bool
#      If True the arrows are automatically scaled to fit the plot
#      (Matplotlib's `quiver(..., scale=None)`).  If False the arrows
#      keep the input magnitude (`scale_units='xy', scale=1`).
#
#  myNorm_max : float
#      Norm threshold: any arrow with magnitude > `myNorm_max` is set to
#      zero before plotting.  This mimics the MATLAB
#      `reduce_field()` routine.
#
#  argImage : array-like, shape (H, W)
#      Image to be displayed in the background.  The contrast limits
#      (``clims``) are set to the min/max of this image - if the image
#      is constant they default to ``[0, 1]``.
#
#  Returns
#  -------
#  fig : matplotlib.figure.Figure
#      The figure that contains the plotted image and the quiver
#      arrows.  The figure is returned so that the caller can further
#      manipulate it if desired.
#
#  Example
#  -------
#  >>> import numpy as np
#  >>> H, W = 100, 80
#  >>> x = np.linspace(0, 2*np.pi, W)
#  >>> y = np.linspace(-1, 1, H)
#  >>> X, Y = np.meshgrid(x, y)
#  >>> vx = -np.sin(Y)  # arbitrary field
#  >>> vy = np.cos(X)
#  >>> img = np.random.rand(H, W)
#  >>> fig = bmFieldPlot2_image(X, Y, vx, vy, autoScaleFlag=True,
#  ...                          myNorm_max=5.0, argImage=img)
#  >>> fig.show()
#
# -------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt


def bmFieldPlot2_image(arg_x, arg_y, arg_vx, arg_vy,
                       autoScaleFlag: bool,
                       myNorm_max: float,
                       argImage):
    """
    Visualise a vector field on top of an image.

    The routine is a lightweight port of the MATLAB function
    `bmFieldPlot2_image`.  It performs the same normalisation of the
    field, reduction of the arrow density, and optional
    transposition, then draws the result with `matplotlib.pyplot.quiver`.

    Parameters
    ----------
    arg_x, arg_y, arg_vx, arg_vy : array-like, shape (H, W)
        Coordinates and vector components.  They are reshaped to the
        image shape and normalised by the grid spacing in X and Y.
    autoScaleFlag : bool
        If True arrows are automatically scaled to fit the plot
        (Matplotlib's `scale=None`).  If False the arrows keep the
        magnitude given by the input vectors (`scale=1`).
    myNorm_max : float
        Any arrow whose Euclidean norm exceeds this value is
        discarded before plotting.
    argImage : array-like, shape (H, W)
        The image on which the arrows will be overlaid.

    Returns
    -------
    fig : matplotlib.figure.Figure
        The figure containing the plotted image and quiver arrows.
    """
    # -------------------- argument preprocessing --------------------
    argImage = np.asarray(argImage, dtype=float)
    if argImage.ndim < 2:
        raise ValueError('argImage must be 2-D')

    H, W = argImage.shape[:2]                 # image size

    nArrow = 20                               # target number of arrows per axis

    # reshape the input arrays to the image shape
    arg_x = np.asarray(arg_x, dtype=float).reshape((H, W))
    arg_y = np.asarray(arg_y, dtype=float).reshape((H, W))
    arg_vx = np.asarray(arg_vx, dtype=float).reshape((H, W))
    arg_vy = np.asarray(arg_vy, dtype=float).reshape((H, W))

    # compute grid spacing from the original coordinates
    dX = abs(arg_x[1, 0] - arg_x[0, 0])      # difference along rows
    dY = abs(arg_y[0, 1] - arg_y[0, 0])      # difference along columns

    # Normalise the vector field by the grid spacing
    arg_vx = arg_vx / dX
    arg_vy = arg_vy / dY

    # Create a 1-based grid that matches the image shape
    # (MATLAB uses 1-based indices; for matplotlib we can keep 0-based)
    x_grid = np.arange(H)
    y_grid = np.arange(W)
    X_grid, Y_grid = np.meshgrid(x_grid, y_grid, indexing='ij')

    # -------------------- preprocessing of the field --------------------
    # 1. Reduce field - keep only a subset of arrows
    def reduce_field(x, y, vx, vy):
        # zero out arrows that are too large
        norms = np.sqrt(vx**2 + vy**2)
        mask = norms <= myNorm_max
        vx = vx * mask
        vy = vy * mask

        # down-sample to roughly nArrow arrows per axis
        step_x = max(H // (nArrow + 1), 1)
        step_y = max(W // (nArrow + 1), 1)
        return x[::step_x, ::step_y], y[::step_x, ::step_y], vx[::step_x, ::step_y], vy[::step_x, ::step_y]

    # 2. Transpose field - optional (not exposed to user, kept for parity)
    def transpose_field(x, y, vx, vy, img):
        # For compatibility with the MATLAB code, this routine swaps
        # the X/Y axes.  We keep it but leave it disabled by default.
        return x, y, vx, vy, img  # unchanged

    # Apply the reductions
    x, y, vx, vy = reduce_field(X_grid, Y_grid, arg_vx, arg_vy)
    x, y, vx, vy, argImage = transpose_field(x, y, vx, vy, argImage)

    # -------------------- plotting ------------------------------------
    # Create a figure (named "bmFieldPlot2") - the figure is returned
    fig = plt.figure(figsize=(6, 6), facecolor='w')
    fig.canvas.manager.set_window_title('bmFieldPlot2')

    # set contrast limits to image range, or 0-1 if constant
    vmin, vmax = argImage.min(), argImage.max()
    if vmin == vmax:
        vmin, vmax = 0.0, 1.0

    ax = fig.add_subplot(111)
    ax.imshow(argImage, cmap='gray', vmin=vmin, vmax=vmax)
    ax.quiver(y, x, vy, vx,
              scale_units='xy',
              scale=1 if not autoScaleFlag else None,
              color='r')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_aspect('equal')
    ax.set_xlim(-0.5, W - 0.5)
    ax.set_ylim(H - 0.5, -0.5)          # flip Y-axis so that image origin is bottom-left

    # add a tiny legend that mimics the MATLAB title
    title = (f'autoScale={autoScaleFlag}  '
             f'myNorm_max={myNorm_max:.2f}  '
             f'constrains=[{vmin:.2f}, {vmax:.2f}]')
    fig.suptitle(title, fontsize=10, y=0.92)

    plt.tight_layout()
    return fig
