"""
Port Python fidèle de bmSparseMat_vec.m

Remarques :
- La logique MATLAB est conservée autant que possible.
- Les fonctions utilitaires MATLAB sont séparées.
- Les fonctions mex sont supposées exister côté Python
  (wrappers natifs, ctypes, pybind11, cffi, etc.).
- Les cas "Case not implemented." du code MATLAB restent non implémentés.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple
import numpy as np


# ============================================================
# Exceptions / utilitaires généraux
# ============================================================

class MatlabError(Exception):
    """Équivalent Python d'un error(...) MATLAB."""
    pass


def error(msg: str) -> None:
    raise MatlabError(msg)


def disp(msg: Any) -> None:
    print(msg)


# ============================================================
# Fonctions utilitaires style MATLAB
# ============================================================

def isempty(x: Any) -> bool:
    """
    Approximation fidèle de isempty MATLAB.
    """
    if x is None:
        return True

    if isinstance(x, (list, tuple, dict, set, str, bytes)):
        return len(x) == 0

    if isinstance(x, np.ndarray):
        return x.size == 0

    # Pour des objets custom : considérer vide si __len__ existe et vaut 0
    try:
        return len(x) == 0
    except TypeError:
        return False


def ndims(x: Any) -> int:
    """
    Équivalent de ndims MATLAB.
    """
    if isinstance(x, np.ndarray):
        return x.ndim

    # Pour listes imbriquées, on force conversion numpy
    try:
        return np.asarray(x).ndim
    except Exception:
        return 0


def strcmp(a: Any, b: Any) -> bool:
    """
    Équivalent simple de strcmp MATLAB.
    """
    return str(a) == str(b)


def islogical(x: Any) -> bool:
    """
    Équivalent de islogical MATLAB.
    """
    return isinstance(x, (bool, np.bool_))


def matlab_class(x: Any) -> str:
    """
    Approximation de class(x) MATLAB.
    Ici on ne gère que ce qui est utile pour ce port.
    """
    if isinstance(x, np.ndarray):
        if x.dtype == np.float32:
            return "single"
        if x.dtype == np.float64:
            return "double"
        if x.dtype == np.complex64:
            return "single"
        if x.dtype == np.complex128:
            return "double"
    return type(x).__name__


def int32(x: Any) -> np.int32:
    return np.int32(x)


def size(x: np.ndarray, dim: Optional[int] = None):
    """
    Approximation de size MATLAB.

    - size(x) -> tuple shape
    - size(x, 1) -> nb lignes
    - size(x, 2) -> nb colonnes

    Convention MATLAB 1-based pour dim.
    """
    arr = np.asarray(x)

    if dim is None:
        return arr.shape

    if dim < 1:
        raise ValueError("MATLAB dimensions start at 1.")

    # En MATLAB, size(x, d) retourne 1 si d > ndims(x)
    if dim > arr.ndim:
        return 1

    return arr.shape[dim - 1]


def real(x: np.ndarray) -> np.ndarray:
    return np.real(x)


def imag(x: np.ndarray) -> np.ndarray:
    return np.imag(x)


# ============================================================
# Stubs / placeholders pour les fonctions mex
# À remplacer par tes wrappers Python réels.
# ============================================================

def bmSparseMat_rR_oBlock_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_rR_oBlock_mex wrapper not provided.")


def bmSparseMat_rR_nBlock_omp_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_rR_nBlock_omp_mex wrapper not provided.")


def bmSparseMat_cR_oBlock_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_cR_oBlock_mex wrapper not provided.")


def bmSparseMat_cR_nBlock_omp_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_cR_nBlock_omp_mex wrapper not provided.")


def bmSparseMat_rC_oBlock_omp_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_rC_oBlock_omp_mex wrapper not provided.")


def bmSparseMat_rC_oBlock_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_rC_oBlock_mex wrapper not provided.")


def bmSparseMat_cC_oBlock_omp_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_cC_oBlock_omp_mex wrapper not provided.")


def bmSparseMat_cC_oBlock_mex(*args, **kwargs):
    raise NotImplementedError("bmSparseMat_cC_oBlock_mex wrapper not provided.")


# ============================================================
# Parsing des flags varargin
# ============================================================

def parse_omp_flag(varargin: Tuple[Any, ...]) -> bool:
    """
    MATLAB:
        varargin{1}: 'omp' ou bool
        default = false
    """
    omp_flag = None

    if len(varargin) > 0:
        arg = varargin[0]
        if strcmp(arg, "omp"):
            omp_flag = True
        elif islogical(arg):
            omp_flag = bool(arg)

    if omp_flag is None:
        omp_flag = False

    return omp_flag


def parse_real_flag(varargin: Tuple[Any, ...]) -> bool:
    """
    MATLAB:
        varargin{2}: 'complex' / 'real' / bool
        default = true ('real')

    R_flag = True  -> réel
    R_flag = False -> complexe
    """
    r_flag = None

    if len(varargin) > 1:
        arg = varargin[1]
        if strcmp(arg, "complex"):
            r_flag = False
        elif strcmp(arg, "real"):
            r_flag = True
        elif islogical(arg):
            r_flag = bool(arg)

    if r_flag is None:
        r_flag = True

    return r_flag


def parse_transpose_flag(v: np.ndarray, varargin: Tuple[Any, ...]) -> Tuple[bool, np.int32]:
    """
    MATLAB:
        varargin{3}: bool ou 'T'
        T_flag = True  -> v contient des vecteurs ligne
        T_flag = False -> v contient des vecteurs colonne

    Retourne:
        (T_flag, n_vec_32)
    """
    t_flag = None

    if len(varargin) > 2:
        arg = varargin[2]

        if arg is True or strcmp(arg, "T"):
            n_vec_32 = int32(size(v, 1))
            t_flag = True
        else:
            n_vec_32 = int32(size(v, 2))
            t_flag = False

        return t_flag, n_vec_32

    # Valeur par défaut : on devine comme en MATLAB
    v_size = size(v)
    if len(v_size) == 1:
        # Cas rare : vecteur 1D
        # On le traite comme colonne par défaut
        return False, int32(1)

    if v_size[0] >= v_size[1]:
        # plus de données que de vecteurs -> vecteurs en colonnes
        return False, int32(size(v, 2))
    else:
        # vecteurs en lignes
        return True, int32(size(v, 1))


# ============================================================
# Validation
# ============================================================

def validate_bmSparseMat_vec_inputs(s: Any, v: np.ndarray) -> None:
    """
    Reprend les checks critiques du MATLAB.
    """
    # Check objet sparse
    if not hasattr(s, "check") or not callable(s.check):
        error("The bmSparseMat object must provide a callable check() method.")
    s.check()

    # Check dimensions de v
    if ndims(v) > 2:
        error("The input list of vectors 'v' is a matrix that cannot have more that 2 dim.")

    # Check type single
    # En MATLAB ici on veut du single.
    # Pour complex, complex64 est la version 'single complexe'.
    if not isinstance(v, np.ndarray):
        error("Input v must be a numpy.ndarray.")

    if v.dtype not in (np.float32, np.complex64):
        error("The class bmSparseMat is for single class only.")

    # Check block_type
    if not strcmp(s.block_type, "one_block") and not strcmp(s.block_type, "multi_block"):
        error("The bmSparseMat is not cpp_prepared.")

    # Check flag
    if not s.check_flag:
        error("The bmSparseMat has check_flag to false.")


def compute_other_flags(s: Any) -> Tuple[bool, bool]:
    """
    Retourne:
        l_squeeze_flag
        one_block_flag
    """
    if isempty(s.l_jump):
        l_squeeze_flag = False
    else:
        l_squeeze_flag = True

    if strcmp(s.block_type, "one_block"):
        one_block_flag = True
    elif strcmp(s.block_type, "multi_block"):
        one_block_flag = False
    else:
        error("Invalid block_type.")

    return l_squeeze_flag, one_block_flag


# ============================================================
# Fonction principale
# ============================================================

def _normalize_varargin(varargin: Any, extra_varargin: Tuple[Any, ...]) -> Tuple[Any, ...]:
    if varargin is None:
        base: Tuple[Any, ...] = tuple()
    elif isinstance(varargin, tuple):
        base = varargin
    elif isinstance(varargin, list):
        base = tuple(varargin)
    else:
        base = (varargin,)
    if extra_varargin:
        base = base + tuple(extra_varargin)
    return base


def bmSparseMat_vec(s: Any, v: np.ndarray, varargin: Any = None, *extra_varargin) -> np.ndarray:
    """
    Port Python fidèle de bmSparseMat_vec.m

    Parameters
    ----------
    s : bmSparseMat-like object
        Objet sparse contenant les attributs utilisés par le code MATLAB.
    v : np.ndarray
        Matrice de vecteurs, de type np.float32 ou np.complex64.
    *varargin :
        varargin[0] : 'omp' ou bool
        varargin[1] : 'real' / 'complex' ou bool
        varargin[2] : bool ou 'T'

    Returns
    -------
    np.ndarray
        Résultat de la multiplication.
    """

    # ========================================================
    # Cas triviaux
    # ========================================================
    if isempty(s):
        return np.array([], dtype=np.float32)

    if isempty(v):
        return np.array([], dtype=np.float32)

    # ========================================================
    # Checks critiques
    # ========================================================
    validate_bmSparseMat_vec_inputs(s, v)

    # ========================================================
    # Flags
    # ========================================================
    normalized_varargin = _normalize_varargin(varargin, extra_varargin)
    omp_flag = parse_omp_flag(normalized_varargin)
    r_flag = parse_real_flag(normalized_varargin)      # True=real, False=complex
    t_flag, n_vec_32 = parse_transpose_flag(v, normalized_varargin)
    l_squeeze_flag, one_block_flag = compute_other_flags(s)

    # ========================================================
    # Appels des fonctions de calcul selon les flags
    # ========================================================

    # --------------------------------------------------------
    # Cas : vecteurs ligne
    # --------------------------------------------------------
    if t_flag:
        # ======================
        # Entrée réelle
        # ======================
        if r_flag:
            if one_block_flag:
                if omp_flag:
                    error("Case not implemented.")
                else:
                    disp("bmSparseMat_rR_oBlock_mex")
                    w = bmSparseMat_rR_oBlock_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        v, n_vec_32
                    )
                    return w

            else:
                if omp_flag:
                    disp("bmSparseMat_rR_nBlock_omp_mex")
                    w = bmSparseMat_rR_nBlock_omp_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        s.nBlock, s.block_length, s.l_block_start, s.m_block_start,
                        v, n_vec_32
                    )
                    return w
                else:
                    error("Case not implemented.")

        # ======================
        # Entrée complexe
        # ======================
        else:
            if one_block_flag:
                if omp_flag:
                    error("Case not implemented.")
                else:
                    disp("bmSparseMat_cR_oBlock_mex")
                    w_real, w_imag = bmSparseMat_cR_oBlock_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        real(v), imag(v), n_vec_32
                    )
                    return w_real + 1j * w_imag

            else:
                if omp_flag:
                    disp("bmSparseMat_cR_nBlock_omp_mex")
                    w_real, w_imag = bmSparseMat_cR_nBlock_omp_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        s.nBlock, s.block_length, s.l_block_start, s.m_block_start,
                        real(v), imag(v), n_vec_32
                    )
                    return w_real + 1j * w_imag
                else:
                    error("Case not implemented")

    # --------------------------------------------------------
    # Cas : vecteurs colonne
    # --------------------------------------------------------
    else:
        # ======================
        # Entrée réelle
        # ======================
        if r_flag:
            if one_block_flag:
                if omp_flag:
                    disp("bmSparseMat_rC_oBlock_omp_mex")
                    w = bmSparseMat_rC_oBlock_omp_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        v, n_vec_32
                    )
                    return w
                else:
                    disp("bmSparseMat_rC_oBlock_mex")
                    w = bmSparseMat_rC_oBlock_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        v, n_vec_32
                    )
                    return w
            else:
                error("Case not implemented")

        # ======================
        # Entrée complexe
        # ======================
        else:
            if one_block_flag:
                if omp_flag:
                    w_real, w_imag = bmSparseMat_cC_oBlock_omp_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        real(v), imag(v), n_vec_32
                    )
                    return w_real + 1j * w_imag
                else:
                    w_real, w_imag = bmSparseMat_cC_oBlock_mex(
                        s.r_size, s.r_jump, s.r_nJump,
                        s.m_val,
                        s.l_size, s.l_jump, s.l_nJump, l_squeeze_flag,
                        real(v), imag(v), n_vec_32
                    )
                    return w_real + 1j * w_imag
            else:
                error("Case not implemented")

    error("Unexpected control flow in bmSparseMat_vec.")
