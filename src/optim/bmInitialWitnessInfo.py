import numpy as np
from src.varargin.bmVarargin import bmVarargin


def _o(witnessInfo, varargin):
    """
    Internal helper that fills the witnessInfo structure with the
    parameters parsed from *varargin* and initial values for the
    objective, data fidelity and regularisation terms.

    The MATLAB version stores the parameters in 1-based cell arrays.
    In Python we simply append to lists.
    """
    # Parse input arguments - bmVarargin returns the values in the
    # correct order.
    (
        function_label,
        N_u,
        n_u,
        dK_u,
        ve_max,
        nIter_max,
        nCGD,
        delta,
        rho,
        regul_mode,
    ) = bmVarargin(varargin)

    # Store the labels and values
    witnessInfo.param_name.append("function_label")
    witnessInfo.param.append(function_label)

    witnessInfo.param_name.append("N_u")
    witnessInfo.param.append(N_u)

    witnessInfo.param_name.append("n_u")
    witnessInfo.param.append(n_u)

    witnessInfo.param_name.append("dK_u")
    witnessInfo.param.append(dK_u)

    witnessInfo.param_name.append("ve_max")
    witnessInfo.param.append(ve_max)

    witnessInfo.param_name.append("nIter_max")
    witnessInfo.param.append(nIter_max)

    witnessInfo.param_name.append("nCGD")
    witnessInfo.param.append(nCGD)

    witnessInfo.param_name.append("delta")
    witnessInfo.param.append(delta)

    witnessInfo.param_name.append("rho")
    witnessInfo.param.append(rho)

    witnessInfo.param_name.append("regul_mode")
    witnessInfo.param.append(regul_mode)

    # Initialise the optimisation history arrays.
    witnessInfo.param_name.append("objective_function")
    witnessInfo.param.append(np.zeros(nIter_max))

    witnessInfo.param_name.append("data_fidelity_term")
    witnessInfo.param.append(np.zeros(nIter_max))

    witnessInfo.param_name.append("regule_term")
    witnessInfo.param.append(np.zeros(nIter_max))


def bmInitialWitnessInfo(witnessInfo, varargin):
    """
    Initialise a WitnessInfo structure for optimisation.
    The function accepts the witnessInfo object and an arbitrary number
    of optional arguments that are parsed by :func:`bmVarargin`.

    Parameters
    ----------
    witnessInfo : object
        Object containing the fields ``param_name`` and ``param``.
    varargin : list
        Optional arguments that are passed to :func:`bmVarargin`.

    Returns
    -------
    witnessInfo
        The same object with its fields updated.
    """
    _o(witnessInfo, varargin)
    return witnessInfo
