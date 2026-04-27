import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmZero import bmZero

def bmImZeroFill(arg_im, N_u, n_u, argType):
    """
    Pad an image array with zeros so that its size matches the desired
    k-space grid size ``N_u``.  The function supports 1-D, 2-D and 3-D
    images with an optional channel dimension.

    Parameters
    ----------
    arg_im : array_like
        Input image data.  The array may contain a channel dimension
        as the last axis.  If the array has no channel dimension
        (``arg_im.shape[:len(n_u)] == tuple(n_u)``) then it is
        interpreted as a single-channel image.

    N_u : array_like
        Desired k-space grid size.  ``N_u`` must be a list or array of
        length 1, 2 or 3.  It is interpreted as the size of the final
        output array in each dimension.

    n_u : array_like
        Current grid size of ``arg_im`` (i.e. the size before padding).
        ``n_u`` can be 1-D, 2-D or 3-D.

    argType : str
        String indicating the desired output dtype.  Valid values are
        ``'real_double'``, ``'real_single'``, ``'complex_double'`` and
        ``'complex_single'``.

    Returns
    -------
    out_im : ndarray
        Zero-padded array of shape ``(*N_u, nCh)`` where ``nCh`` is the
        number of channels in ``arg_im``.  The dtype is inferred from
        ``argType``.

    Notes
    -----
    The padding is performed exactly as MATLAB would do it, i.e. the
    image is centred on the output array.  The indices are computed
    using integer arithmetic that reproduces the MATLAB formulas

    .. math::

        \\text{ind}_x = \\left(\\frac{N_x}{2}+1-\\frac{n_x}{2}\\right)
                      :\\left(\\frac{N_x}{2}+1+\\frac{n_x}{2}-1\\right)

    and analogous expressions for the other dimensions.
    """
    # ------------------------------------------------------------------
    # 1. Normalise input shapes
    # ------------------------------------------------------------------
    N_u = np.asarray(N_u, dtype=int).flatten()
    n_u = np.asarray(n_u, dtype=int).flatten()
    arg_im = np.asarray(arg_im)

    im_dim = len(n_u)          # 1, 2 or 3
    n_ch = 1

    # 2-D and 3-D images will have an extra channel dimension
    if arg_im.ndim == im_dim:
        n_ch = 1
    else:
        n_ch = arg_im.shape[-1]

    # reshape arg_im so that the first ``im_dim`` dimensions match ``n_u``
    if n_ch == 1:
        arg_im = np.reshape(arg_im, tuple(n_u))
    else:
        arg_im = np.reshape(arg_im, tuple(n_u) + (n_ch,))

    # ------------------------------------------------------------------
    # 3. Create output array with the correct dtype
    # ------------------------------------------------------------------
    dtype_map = {
        'real_double'  : np.float64,
        'real_single'  : np.float32,
        'complex_double': np.complex128,
        'complex_single': np.complex64
    }

    if argType not in dtype_map:
        raise ValueError(f'Unsupported argType {argType!r}')

    out_shape = tuple(N_u) + (n_ch,)
    out_im = np.zeros(out_shape, dtype=dtype_map[argType])

    # ------------------------------------------------------------------
    # 4. Compute centred slices for each dimension
    # ------------------------------------------------------------------
    def centred_slice(size, target):
        """
        Return a Python slice that selects ``target`` contiguous
        elements centred in an array of length ``size``.
        """
        center = size // 2                      # 0-based centre index
        half_target = target // 2
        start = center - half_target
        end_inclusive = center + half_target + (target % 2 == 1) - 1
        return slice(start, end_inclusive + 1)   # end exclusive

    if im_dim == 1:
        slice_x = centred_slice(N_u[0], n_u[0])
        out_im[slice_x] = arg_im

    elif im_dim == 2:
        slice_x = centred_slice(N_u[0], n_u[0])
        slice_y = centred_slice(N_u[1], n_u[1])
        out_im[slice_x, slice_y] = arg_im

    elif im_dim == 3:
        slice_x = centred_slice(N_u[0], n_u[0])
        slice_y = centred_slice(N_u[1], n_u[1])
        slice_z = centred_slice(N_u[2], n_u[2])
        out_im[slice_x, slice_y, slice_z] = arg_im

    else:
        raise ValueError(f'Unsupported dimensionality {im_dim} for n_u')

    return out_im

# The function ``bmZero`` is intentionally not used in this implementation
# to avoid relying on the original helper.  The ``bmZero`` import is kept
# for backward compatibility with modules that expect it to be present.
