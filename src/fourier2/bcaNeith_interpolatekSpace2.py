from __future__ import annotations
from third_part.matlab_compat.matlab_native import isempty, size


def bcaNeith_interpolatekSpace(kspace, interp_kerns, kern_types, kernel):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # 
    # Berk Can Acikgoz
    # University of Bern and Insel Spital
    # Bern - Switzerland
    # February 2025
    # 
    # This is the function where the missing k-space lines are filled with the
    # acquired lines interpolated with already extracted interpolation
    # kernels (interp_kerns)
    # Once filled, needs to be added on
    # top of the already acquired k-space
    # Create a mask over extracted k-space neighborhood and
    # determine which interpolator is suitable among the
    # interp_kerns
    # kspace_kern_mask = normalize(kspace_kern_mask, 'norm');
    # 
    # since we do not have an interpolator for it
    # this check practically does nothing. Only as a
    # safety check for zero-filled k-spaces...
    # (denoted with M)
    # Extract the line to be interpolated (calib_inp) with M, do the
    # forward operation (M*calib_inp) and save the interpolated lines
    # to their appropriate locations in kspace_interp
    # 
    # acquired one. There is no overlap!
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: [Nx,Ny,~] = size(kspace);  % Extract data size
    # MATLAB: Nxk = kernel(1); % Extract kernel
    # MATLAB: Nyk = kernel(2); % sizes
    # MATLAB: xstride = (Nxk-1)/2; % Setting the
    # MATLAB: xm = (Nxk+1)/2;      % properties of how
    # MATLAB: ystride = (Nyk-1)/2; % kernel is
    # MATLAB: ym = (Nyk+1)/2;      % convolved
    # MATLAB: kspace_interp = zeros(size(kspace)); % Initialize the "interpolated" k-space.
    # MATLAB: for x = 1+xstride:Nx-xstride
    # MATLAB: for y = 1+ystride:Ny-ystride
    # MATLAB: if kspace(x,y)==0  % Check if the current position data is missing
    # MATLAB: kspace_kern = ...  % Extract the k-space around the current
    # MATLAB: ...  % k-space point using the kernel
    # MATLAB: kspace(x-xstride:x+xstride, y-ystride:y+ystride);
    # MATLAB: kspace_kern_mask = (abs(kspace_kern)>0);
    # MATLAB: kspace_kern_mask = 1*kspace_kern_mask(:);
    # MATLAB: kspace_kern_mask = kspace_kern_mask*sqrt(1/(kspace_kern_mask'*kspace_kern_mask));
    # MATLAB: type = find(abs((kern_types'*kspace_kern_mask) - 1)<1e-9);
    # MATLAB: kern_mask = reshape(kspace_kern_mask, kernel);
    # MATLAB: if isempty(type)  % Do nothing if there is no matching kernel type
    # MATLAB: else
    # MATLAB: M = interp_kerns{type}; % Extract the suitable interpolator
    # MATLAB: calib_inp = [];
    # MATLAB: for xx = -xstride:xstride
    # MATLAB: for yy = -ystride:ystride
    # MATLAB: if kern_mask(xx+xm,yy+ym)>0
    # MATLAB: calib_inp = [calib_inp;squeeze(kspace(x+xx,y+yy,:))];
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: kspace_interp(x,y,:)=M*calib_inp;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # MATLAB: res = kspace_interp+kspace; % Add the interpolated k-space to the
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    res = None
    kspace_interp = None
    return res, kspace_interp

# Auto-generated entrypoint alias for import compatibility
bcaNeith_interpolatekSpace2 = bcaNeith_interpolatekSpace
