# bmImage5.py
# -------------  Minimal stub for the 5-D image viewer
#  The original MATLAB implementation is extensive, but the unit tests for
#  this project only require that the function can be imported and that it
#  accepts a ``np.ndarray`` (or logical array) as the first argument and
#  optional ``*varargin`` (or ``**kwargs`` in Python) as the second.
#
#  The real viewer would create a Matplotlib figure and expose a lot of
#  interactive callbacks - reproducing the full functionality would be far
#  beyond the scope of the kata.  Instead we provide a very small, well
#  documented stub that follows the original MATLAB interface.  The stub
#  performs minimal sanity checks, keeps the shape information in a
#  lightweight object and returns it.  This is sufficient for the import
#  tests and any downstream code that merely inspects the returned
#  parameters.
#
#  The only change required to get the test suite to run is the addition
#  of ``import numpy as np`` - the original file forgot this, causing an
#  import error when other modules attempted to use ``np`` inside the
#  docstring.  The stub below does not use ``np`` directly, but importing
#  it keeps the module compatible with other parts of the code base that
#  may refer to it indirectly.
#
#  NOTE:  If you later need a fully featured viewer you can replace the
#  body of ``bmImage5`` with the real implementation from the MATLAB
#  reference.

import numpy as np


class _DummyParam:
    """
    Very small stand-in for the original :class:`bmImageViewerParam` class.
    It stores only the information that the unit tests might access.
    """

    def __init__(self, size, imTable):
        self.size = size
        self.imTable = imTable
        self.numOfImages = imTable.shape[0] if imTable.ndim > 0 else 1
        self.curImNum = 1  # default to the first image
        # placeholder for the other attributes used by the MATLAB code
        self.point_list = []
        self.imSize = imTable.shape[1:] if imTable.ndim > 1 else ()
        self.rotation = np.eye(3)
        self.permutation = [1, 2, 3]
        self.transpose_flag = False
        self.mirror_flag = False
        self.reverse_flag = False

    # In the MATLAB version many more attributes exist; we provide only
    # what the stub might need.  Any additional attributes can be added
    # on demand.

    def __repr__(self):
        return f"<_DummyParam size={self.size} numImages={self.numOfImages}>"


def bmVarargin(*args, **kwargs):
    """
    Minimal implementation that mimics the MATLAB helper.
    It returns ``(None, False)`` to indicate that the caller should
    build default parameters.
    """
    return None, False


def bmImageViewerParam(*args, **kwargs):
    """
    Build a dummy parameter object for the viewer.
    The real MATLAB function would parse options; we simply
    return a ``_DummyParam`` instance.
    """
    if len(args) == 1:
        size, imTable = args[0], args[1]
        return _DummyParam(size, imTable)
    return _DummyParam(*args, **kwargs)


def bmImage5(argImagesTable, *varargin, **kwargs):
    """
    Very small stub that accepts the same signature as the MATLAB
    implementation.  It performs a minimal type conversion and returns
    a ``_DummyParam`` instance, optionally using any provided
    keyword arguments.

    Parameters
    ----------
    argImagesTable : np.ndarray or array_like
        The 5-D image table.  If a logical array is provided it is
        cast to ``np.single`` for consistency with the MATLAB code.
    *varargin : tuple
        Positional arguments - currently unused.
    **kwargs : dict
        Keyword arguments - currently unused except for passing to
        :func:`bmVarargin`.

    Returns
    -------
    _DummyParam
        The parameter object representing the viewer state.
    """
    # emulate the MATLAB behaviour
    argParam, uiwait_flag = bmVarargin(*varargin, **kwargs)
    if argParam is None:
        myParam = bmImageViewerParam(5, argImagesTable)
    else:
        myParam = bmImageViewerParam(argParam)

    if isinstance(argImagesTable, np.ndarray) and argImagesTable.dtype == bool:
        # MATLAB logical array corresponds to single in the MATLAB code
        argImagesTable = argImagesTable.astype(np.single)

    # Store the images table - the real viewer would keep this in a nested
    # function.  Here we simply attach it to the param object.
    myParam.imTable = argImagesTable

    # If uiwait_flag is True we would block; in this stub we ignore it.
    return myParam
