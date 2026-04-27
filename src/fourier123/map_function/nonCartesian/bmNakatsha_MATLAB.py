from __future__ import annotations
from third_part.matlab_compat.matlab_native import double, isempty, size
from porting.lib.utils import int32, strcmp


def bmNakatsha_MATLAB(y, G, KFC_conj, C_flag, n_u):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # x = bmNakatsha_MATLAB(y, G, KFC_conj, C_flag, n_u)
    # 
    # This function copmutes the conjugate transpose of the Fourier transform
    # and the coil sensitvity of Y -> C*F*(Y) while gridding the points to the
    # uniform grid.
    # 
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # 
    # Contributors:
    # Dominik Helbing (Documentation & Comments)
    # MattechLab 2024
    # 
    # Parameters:
    # y (array): The data in the k-space to be gridded and transformed into
    # the image space.
    # G (bmSparseMat): The backward gridding sparse matrix which is used for
    # transposing the conjugate. -> Gut
    # KFC_conj (array): The kernel matrix used for deapodization multiplied
    # with the conjugate Fourier factor and the conjugate transpose of the
    # coil sensitivity. Can be missing the conjugate transpose of C.
    # C_flag (logical): Indicates if KFC_conj contains the conjugate of C. If
    # false, the conjugate is not included in KFC_conj.
    # n_u (list): The size of the image space grid.
    # 
    # Returns:
    # x (array): The computed image space data (C*F*y = x). Combined into one
    # image x if C_flag is true, otherwise x has an image for every coil.
    # 
    # Notes:
    # This comes from F(Cx) = y -> x = F*(C*y). If the coil sensitivity is
    # not given in KFC_conj, then only y -> F*(y) = x is computed. The data
    # needs to be multiplied by the volume elements for correct results.
    # 
    # Examples:
    # x = bmNakatsha_MATLAB(y, Gut, KFC_conj, C_flag, n_u);
    # Initialize arguments
    # Set default value if empty
    # Use G.N_u if n_u is empty
    # Convert variables to the correct format
    # Check format and throw errors if something is found
    # Compute C*F*Y
    # Do sparse matrix multiplication to map the data (y) onto the grid defined
    # by G.N_u (gridding)
    # Do inverse FFT for every dimension in block format
    # Return to column format
    # Crop data if needed (N_u > n_u)
    # Reduce smoothing effect introduced by gridding using a window to grid the
    # data -> deapodization, multiply with coil sensitivity
    # Eventual channel reduction if KFC_conj contains C_conj
    # Helper function
    # This function checks that all inputs have the correct type, size and
    # values needed for the computation to work. Throws errors if something
    # amiss is found.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if isempty(C_flag)
    # MATLAB: C_flag = false;
    # MATLAB: end
    # MATLAB: if isempty(n_u)
    # MATLAB: n_u = G.N_u;
    # MATLAB: end
    # MATLAB: N_u     = double(int32(G.N_u(:)'));
    # MATLAB: n_u     = double(int32(n_u(:)'));
    # MATLAB: nPt     = double(G.r_size);
    # MATLAB: imDim   = size(N_u(:), 1);
    # MATLAB: nCh     = size(y, 2);
    # MATLAB: private_check(y, G, KFC_conj, N_u, n_u, nCh, nPt, C_flag);
    # MATLAB: x = bmSparseMat_vec(G, y, 'omp', 'complex', false);
    # MATLAB: x = bmBlockReshape(x, N_u);
    # MATLAB: for n = 1:3
    # MATLAB: if imDim > (n-1)
    # MATLAB: x = fftshift(ifft(ifftshift(x, n), [], n), n);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: x = bmColReshape(x, N_u);
    # MATLAB: if ~isequal(N_u, n_u)
    # MATLAB: x = bmBlockReshape(x, N_u);
    # MATLAB: x = bmImCrope(x, N_u, n_u);
    # MATLAB: x = bmColReshape(x, n_u);
    # MATLAB: end
    # MATLAB: x = x.*KFC_conj;
    # MATLAB: if C_flag
    # MATLAB: x = sum(x, 2);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: if not(isa(y, 'single'))
    # MATLAB: error('The data''y'' must be of class single');
    # MATLAB: end
    # MATLAB: if not(isa(KFC_conj, 'single'))
    # MATLAB: error('The matrix ''KFC_conj'' must be of class single');
    # MATLAB: end
    # MATLAB: if not(isequal(size(y), [nPt, nCh]))
    # MATLAB: error('The data matrix ''y'' is not in the correct size');
    # MATLAB: end
    # MATLAB: if C_flag
    # MATLAB: if not(isequal(size(KFC_conj), [prod(n_u(:)), nCh] ))
    # MATLAB: error('The matrix ''C'' is not in the correct size');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: if sum(mod(N_u(:), 2)) > 0
    # MATLAB: error('N_u must have all components even for the Fourier transform. ');
    # MATLAB: end
    # MATLAB: if sum(mod(n_u(:), 2)) > 0
    # MATLAB: error('n_u must have all components even for the Fourier transform. ');
    # MATLAB: end
    # MATLAB: if not(strcmp(G.block_type, 'one_block'))
    # MATLAB: error('The block type of G must be ''one_block''. ');
    # MATLAB: end
    # MATLAB: if strcmp(class(G), 'bmSparseMat')
    # MATLAB: if not(strcmp(G.type, 'cpp_prepared')) && not(strcmp(G.type, 'l_squeezed_cpp_prepared'))
    # MATLAB: error('G is bmSparseMat but is not cpp_prepared. ');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    x = None
    return x
