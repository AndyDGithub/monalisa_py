# MATLAB -> Python Reference Transformations

Use these as style anchors during repair. Do not output placeholders when the MATLAB source is non-trivial.

## Example 1: `bmSparseMat_vec_2` (branch-heavy dispatcher)

MATLAB excerpt:
```matlab
if not(strcmp(class(s), 'bmSparseMat')) && strcmp(class(v), 'double')
    w = s*v;
    return;
end

if T_flag
    if R_flag
        if one_block_flag
            w = bmSparseMat_rR_oBlock_mex(...);
```

Python pattern:
```python
if s_class != "bmSparseMat" and v_class == "double":
    return s * v_arr

if t_flag:
    if r_flag:
        if one_block_flag:
            return bmSparseMat_rR_oBlock_mex(...)
```

Key mapping:
- keep MATLAB branch structure explicit (`if/elif/else`), avoid collapsing logic.
- convert MATLAB flags (`T_flag`, `R_flag`, `omp_flag`) into clear booleans before dispatch.
- keep mex calls as explicit call sites; if wrapper is missing, raise `NotImplementedError` from wrapper, not TODO markers.

## Example 2: `DataFromISMRMRD` (I/O + XML extraction)

MATLAB excerpt:
```matlab
myData = h5read(filePath, '/dataset/data');
myXML = h5read(filePath, '/dataset/xml');
xFoV = str2double(xmlDoc.getElementsByTagName('x').item(1).getTextContent());
```

Python pattern:
```python
with h5py.File(file_path, "r") as h5_file:
    raw_data, head, xml_text = _read_dataset_data(h5_file)
fov, fov_recon = _extract_fov_from_xml(xml_text)
```

Key mapping:
- move script-side effects to return values (dictionary/dataclass summary).
- isolate parsing in helpers (`_extract_fov_from_xml`, `_to_scalar`) for deterministic tests.
- keep numerical pipeline steps close to MATLAB order.

## Example 3: `varargin` handling

MATLAB:
```matlab
if ~isempty(varargin)
    if strcmp(varargin{1}, 'omp')
        omp_flag = true;
```

Python:
```python
args = _as_varargin(varargin)
omp_flag = False
if args:
    first = args[0]
    if first == "omp":
        omp_flag = True
```

Key mapping:
- normalize optional args once (`tuple/list/scalar -> tuple`), then parse flags.
- keep defaults explicit and close to MATLAB defaults.


## Example 4: `bmSave` (non native behavior function - inputname)
MATLAB:
```matlab
% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023

function bmSave(arg_file, arg_var)

myName = inputname(2); 
eval([myName, ' = arg_var; ']); 
save(arg_file, myName, '-v7.3'); 

end
```

Python:
```python
import scipy.io
from third_part.matlab_compat.matlab_runtime_metadata import resolve_inputname


def bmSave(arg_file, arg_var, *, var_name=None):
    my_name = resolve_inputname(
        2,
        args=(arg_file, arg_var),
        explicit_name=var_name,
        fallback_name="arg_var",
        frame_depth=2,
    )
    scipy.io.savemat(arg_file, {my_name: arg_var})
    return None
```



## Example 5: `bmFourierOfGauss_function` (discared argument)
MATLAB:
```matlab
% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023

function Ff = bmFourierOfGauss_function(~, myMu, mySigma)

Ff = exp(-2*pi^2*mySigma^2*k.^2).*exp(-i1*2*pi*myMu*k); 

end
```

Python:
```python
from __future__ import annotations

import numpy as np


def bmFourierOfGauss_function(unused, myMu, mySigma):
    """Robust placeholder for a MATLAB source that references undefined symbols.

    Original MATLAB uses undefined identifiers (`k`, `i1`), so a strict 1:1 port is
    impossible without guessing hidden workspace assumptions. We interpret the first
    argument as `k` when available, otherwise fall back to `k=0`.
    """
    if unused is None:
        k = np.asarray(0.0)
    else:
        k = np.asarray(unused)
    ff = np.exp(-2.0 * (np.pi**2) * (mySigma**2) * (k**2)) * np.exp(-1j * 2.0 * np.pi * myMu * k)
    return ff
```


## Example 6: `bmFieldPlot2_noImage` (very long file with embedded function)
MATLAB:
```matlab
% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023

function bmFieldPlot2_noImage(arg_x, arg_y, arg_vx, arg_vy, argSize, autoScaleFlag, myNorm_max)

% argin initial -----------------------------------------------------------


argSize = argSize(:)';
argSize = argSize(1, 1:2);

nArrow = 20;

arg_x = reshape(arg_x, argSize);
arg_y = reshape(arg_y, argSize);
arg_vx = reshape(arg_vx, argSize);
arg_vy = reshape(arg_vy, argSize);


transpose_flag = false; 

x = []; 
y = []; 
vx = []; 
vy = []; 


mySize = argSize; 

update_field; 

% END_argin initial -------------------------------------------------------




% graphic initial ---------------------------------------------------------

controlFlag     = 0;
shiftFlag       = 0;
escFlag         = 0;

reverse_flag = false; 
mirror_flag  = false;

reverse_string = 'off'; 
transpose_string = 'off'; 
mirror_string = 'off';

x_label = 'X';
y_label = 'Y'; 


myFigure = figure(  'Name', 'bmFieldPlot2', ...
    'WindowScrollWheelFcn', @myWindowScrollWheelFcn,...
    'keyreleasefcn', @myKeyReleaseFcn,...
    'keypressfcn', @myKeyPressFcn,...
    'WindowButtonDownFcn', @myClickCallback);


refresh;

% END_graphic initial -----------------------------------------------------

    function myKeyReleaseFcn(~,command) % nested function
        % Switch through the type of key that has been pressed and chose
        % the action to perform
        switch lower(command.Key)
            case 'control'     % Ctrl key is released
                controlFlag = 0;
            case 'shift'       % Shift key is released
                shiftFlag = 0;
            case 'escape'      % Escape key is released
                escFlag = 0;
        end
    end


    function myKeyPressFcn(~,command) % nested function
        switch lower(command.Key)
            case 'control'     % Ctrl key is pressed
                controlFlag = 1;
            case 'shift'       % Shift key is pressed
                shiftFlag = 1;
            case 'escape'      % Escape key is pressed
                escFlag = 1;
            case 'a'
                if controlFlag && shiftFlag
                    autoScaleFlag = not(autoScaleFlag);
                    refresh;
                    shiftFlag = 0; 
                    controlFlag = 0;
                end
            case 'n'
                if controlFlag && shiftFlag
                    
                    myNorm_max = bmGetNum;
                    update_field;
                    refresh;
                    controlFlag = 0;
                    shiftFlag = 0;
                end
            case 'm'
                if controlFlag && shiftFlag
                    
                    mirror_flag = not(mirror_flag);
                    if mirror_flag
                        mirror_string = 'on';
                    else
                        mirror_string = 'off';
                    end
                    
                    refresh;
                    controlFlag = 0;
                    shiftFlag = 0;
                end
            case 'r'
                if controlFlag && shiftFlag
                    
                    reverse_flag = not(reverse_flag);
                    if reverse_flag
                        reverse_string = 'on'; 
                    else
                        reverse_string = 'off';
                    end
                    
                    refresh;
                    controlFlag = 0;
                    shiftFlag = 0;
                end
            case 't'
                if controlFlag && shiftFlag
                    
                    transpose_flag = not(transpose_flag);
                    
                    update_field;
                    refresh;
                    controlFlag = 0;
                    shiftFlag = 0;
                end
        end % End Switch command.key
    end

    function myClickCallback(~, ~)
        
        myCoordinates = get(gca,'CurrentPoint');
        myCoordinates = ceil(myCoordinates(1,1:2)-[0.5 0.5]);
        myX = myCoordinates(2);
        myY = myCoordinates(1);
        
        switch get(gcf,'selectiontype')
            case 'normal'%left mouse button click
                1+1;
            case 'alt'%right mouse button click
                1+1;
        end
    end

    function reset_field()
        x = arg_x;
        y = arg_y;
        
        
        vx = arg_vx;
        vy = arg_vy;
        
        mySize = argSize; 
        
        x_label = 'X'; 
        y_label = 'Y'; 
        
        
        
        
        transpose_string = 'off'; 
    end


    function reduce_field()
        
        myNorm = sqrt(vx(:).^2 + vy(:).^2);
        myNorm(isinf(myNorm)) = 0;
        myNorm(isnan(myNorm)) = 0;
        
        vx(myNorm > myNorm_max) = 0;
        vy(myNorm > myNorm_max) = 0;
        
        
        nPart_1 = fix(argSize(1, 1)/(nArrow+1)) + 1;
        nPart_2 = fix(argSize(1, 2)/(nArrow+1)) + 1;
        
        x =  x(1:nPart_1:end, 1:nPart_2:end);
        y =  y(1:nPart_1:end, 1:nPart_2:end);
        
        
        vx =  vx(1:nPart_1:end, 1:nPart_2:end);
        vy =  vy(1:nPart_1:end, 1:nPart_2:end);
    end


    function transpose_field()
       if transpose_flag
        
           temp = x; 
           x = y; 
           y = temp; 
           
           temp = vx; 
           vx = vy;
           vy = temp; 
           
           x = permute(x, [2, 1]); 
           y = permute(y, [2, 1]);
           vx = permute(vx, [2, 1]); 
           vy = permute(vy, [2, 1]);
           
           mySize = [mySize(1, 2), mySize(1, 1)]; 
           
           temp = x_label;
           x_label = y_label;
           y_label = temp;
           
           
           
           transpose_string = 'on';
           
       end
    end



    function update_field()        
        
        reset_field;
        reduce_field;
        transpose_field; 
        
    end



    function refresh()
        
        figure(myFigure);
        
        
        
        
        if autoScaleFlag
            quiver(y, x, vy, vx, 'Linewidth', 2, 'Autoscale', 'on');
        else
            quiver(y, x, vy, vx, 'Linewidth', 2, 'Autoscale', 'off');
        end        
        
        hold off
        
        if mirror_flag
            set(gca, 'XDir', 'reverse');
        else
            set(gca, 'XDir', 'normal');
        end
        
        if reverse_flag
            set(gca, 'YDir', 'normal');
        else
            set(gca, 'YDir', 'reverse');
        end
        
        axis image
        colormap gray
        myTitle = [ 'Autoscale : ', num2str(autoScaleFlag), ...
                    ', normMax : ', num2str(myNorm_max),...
                    '; reverse : ', reverse_string, ...
                    '; transpose : ', transpose_string];
        
        
                
        title(myTitle);
        
        clim([-1, 0]);
        xlabel(y_label); 
        ylabel(x_label); 
        
    end
end
```

Python:
```python
import numpy as np
import matplotlib.pyplot as plt

def bmFieldPlot2_noImage(arg_x, arg_y, arg_vx, arg_vy, argSize, autoScaleFlag, myNorm_max):
    # argin initial
    argSize = np.array(argSize).reshape(-1)
    argSize = argSize[:2]
    nArrow = 20
    arg_x = np.reshape(arg_x, argSize)
    arg_y = np.reshape(arg_y, argSize)
    arg_vx = np.reshape(arg_vx, argSize)
    arg_vy = np.reshape(arg_vy, argSize)

    # internal variables
    x, y, vx, vy = None, None, None, None
    mySize = argSize
    transpose_flag = False

    # function to reset field
    def reset_field():
        nonlocal x, y, vx, vy, mySize, x_label, y_label, transpose_string
        x = arg_x.copy()
        y = arg_y.copy()
        vx = arg_vx.copy()
        vy = arg_vy.copy()
        mySize = argSize.copy()
        x_label = 'X'
        y_label = 'Y'
        transpose_string = 'off'

    # function to reduce field
    def reduce_field():
        nonlocal x, y, vx, vy
        myNorm = np.sqrt(vx**2 + vy**2)
        myNorm[np.isinf(myNorm)] = 0
        myNorm[np.isnan(myNorm)] = 0
        vx[myNorm > myNorm_max] = 0
        vy[myNorm > myNorm_max] = 0
        nPart_1 = int(np.fix(argSize[0] / (nArrow+1))) + 1
        nPart_2 = int(np.fix(argSize[1] / (nArrow+1))) + 1
        x = x[::nPart_1, ::nPart_2]
        y = y[::nPart_1, ::nPart_2]
        vx = vx[::nPart_1, ::nPart_2]
        vy = vy[::nPart_1, ::nPart_2]

    # function to transpose field
    def transpose_field():
        nonlocal x, y, vx, vy, mySize, x_label, y_label, transpose_string
        if transpose_flag:
            x, y = y, x
            vx, vy = vy, vx
            x = x.T
            y = y.T
            vx = vx.T
            vy = vy.T
            mySize = mySize[::-1]
            x_label, y_label = y_label, x_label
            transpose_string = 'on'

    # update field
    def update_field():
        reset_field()
        reduce_field()
        transpose_field()

    # initial update
    update_field()

    # create figure
    fig, ax = plt.subplots()
    fig.canvas.set_window_title('bmFieldPlot2')
    # event handling functions
    controlFlag, shiftFlag, escFlag = 0, 0, 0
    reverse_flag, mirror_flag = False, False
    reverse_string, transpose_string, mirror_string = 'off', 'off', 'off'
    x_label, y_label = 'X', 'Y'

    def on_key(event):
        nonlocal controlFlag, shiftFlag, escFlag, autoScaleFlag, myNorm_max, mirror_flag, mirror_string
        if event.key == 'control':
            controlFlag = 1
        elif event.key == 'shift':
            shiftFlag = 1
        elif event.key == 'escape':
            escFlag = 1
        elif event.key == 'a':
            if controlFlag and shiftFlag:
                autoScaleFlag = not autoScaleFlag
                refresh()
                shiftFlag = 0
                controlFlag = 0
        elif event.key == 'n':
            if controlFlag and shiftFlag:
                myNorm_max = np.max(np.sqrt(vx**2 + vy**2))
                update_field()
                refresh()
                controlFlag = 0
                shiftFlag = 0
        elif event.key == 'm':
            if controlFlag and shiftFlag:
                mirror_flag = not mirror_flag
                mirror_string = 'on' if mirror_flag else 'off'
                refresh()
                controlFlag = 0
                shiftFlag = 0

    def on_key_release(event):
        nonlocal controlFlag, shiftFlag, escFlag
        if event.key == 'control':
            controlFlag = 0
        elif event.key == 'shift':
            shiftFlag = 0
        elif event.key == 'escape':
            escFlag = 0

    fig.canvas.mpl_connect('key_press_event', on_key)
    fig.canvas.mpl_connect('key_release_event', on_key_release)

    def refresh():
        fig.clear()
        ax = fig.add_subplot(111)
        ax.quiver(y, x, vy, vx, angles='xy', scale_units='xy', scale=1, width=0.003, color='black')
        ax.set_aspect('equal')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        if mirror_flag:
            ax.set_xlim(ax.get_xlim()[::-1])
        else:
            ax.set_xlim(ax.get_xlim())
        if reverse_flag:
            ax.set_ylim(ax.get_ylim())
        else:
            ax.set_ylim(ax.get_ylim()[::-1])
        ax.set_title(f'Autoscale : {int(autoScaleFlag)}, normMax : {myNorm_max}; reverse : {reverse_string}; transpose : {transpose_string}')
        ax.set_xlabel(y_label)
        ax.set_ylabel(x_label)

    # initial refresh
    refresh()
```



## Example 7: `HarmonicField3D` (complexe with numpy)
MATLAB:
```matlab


% 
% Berk Can Acikgoz
% University of Bern and Insel Spital
% Bern - Switzerland
% February 2025
% 


function phi = HarmonicField3D(coeffs, X, Y, Z)
% coeffs: 15x1 vector of basis coefficients
% X, Y, Z: 3D grids from ndgrid
% phi: result scalar field of same size as X/Y/Z

    if numel(coeffs) ~= 15
        error('Expected 15 coefficients');
    end

    r2 = X.^2 + Y.^2 + Z.^2;  % radial term

    % Basis functions
    B = cell(15,1);
    B{1}  = ones(size(X));                      % 1
    B{2}  = X;                                  % x
    B{3}  = Y;                                  % y
    B{4}  = Z;                                  % z
    B{5}  = X .* Y;                             % xy
    B{6}  = X .* Z;                             % xz
    B{7}  = Y .* Z;                             % yz
    B{8}  = X.^2 - Y.^2;                        % x^2 - y^2
    B{9}  = 2 * Z.^2 - X.^2 - Y.^2;             % 2z^2 - x^2 - y^2
    B{10} = X .* (5 * Z.^2 - r2);               % x(5z^2 - r^2)
    B{11} = Y .* (5 * Z.^2 - r2);               % y(5z^2 - r^2)
    B{12} = Z .* (5 * Z.^2 - 3 * r2);           % z(5z^2 - 3r^2)
    B{13} = X .* Y .* Z;                        % xyz
    B{14} = X.^3 - 3 * X .* Y.^2;               % x^3 - 3xy^2
    B{15} = Y.^3 - 3 * X.^2 .* Y;               % y^3 - 3x^2y

    % Weighted sum
    phi = zeros(size(X));
    for i = 1:15
        phi = phi + coeffs(i) * B{i};
    end
end
```


Python:
```python
from __future__ import annotations
import numpy as np


def HarmonicField3D(coeffs, X, Y, Z):
    """Compute the 3D harmonic basis field from 15 coefficients."""
    #
    # Berk Can Acikgoz
    # University of Bern and Insel Spital
    # Bern - Switzerland
    # February 2025
    #
    # coeffs: 15x1 vector of basis coefficients
    # X, Y, Z: 3D grids from ndgrid
    # phi: result scalar field of same size as X/Y/Z

    coeffs_arr = np.asarray(coeffs).reshape(-1)
    if coeffs_arr.size != 15:
        raise ValueError("Expected 15 coefficients")

    X_arr = np.asarray(X)
    Y_arr = np.asarray(Y)
    Z_arr = np.asarray(Z)
    if X_arr.shape != Y_arr.shape or X_arr.shape != Z_arr.shape:
        raise ValueError("X, Y and Z must have the same shape")

    r2 = X_arr**2 + Y_arr**2 + Z_arr**2

    basis = [
        np.ones_like(X_arr),                    # 1
        X_arr,                                  # x
        Y_arr,                                  # y
        Z_arr,                                  # z
        X_arr * Y_arr,                          # xy
        X_arr * Z_arr,                          # xz
        Y_arr * Z_arr,                          # yz
        X_arr**2 - Y_arr**2,                    # x^2 - y^2
        2 * Z_arr**2 - X_arr**2 - Y_arr**2,    # 2z^2 - x^2 - y^2
        X_arr * (5 * Z_arr**2 - r2),            # x(5z^2 - r^2)
        Y_arr * (5 * Z_arr**2 - r2),            # y(5z^2 - r^2)
        Z_arr * (5 * Z_arr**2 - 3 * r2),        # z(5z^2 - 3r^2)
        X_arr * Y_arr * Z_arr,                  # xyz
        X_arr**3 - 3 * X_arr * Y_arr**2,        # x^3 - 3xy^2
        Y_arr**3 - 3 * X_arr**2 * Y_arr,        # y^3 - 3x^2y
    ]

    phi = np.zeros_like(X_arr, dtype=np.result_type(coeffs_arr, X_arr, Y_arr, Z_arr))
    for i in range(15):
        phi = phi + coeffs_arr[i] * basis[i]

    return phi
```


## Example 8: `bcaNeith3` (multi function definition)
MATLAB:
```matlab

% 
% Berk Can Acikgoz
% University of Bern and Insel Spital
% Bern - Switzerland
% February 2025
% 


%%% This is where all the calls to the other functions are done and real
%%% action happens!

function res = MATLABGrappa(kspace, calib, kern)


    padsize = (kern-1)/2;                           % Padding the k-space first 
                                                    % so that edge of the   
    kspace = padarray(kspace, [padsize 0],0);  % k-space is also filled, 
                                                    % otherwise kernel 
                                                    % cannot move at the edge
    

    %%% Call the main functionality functions one by one
    kern_types = bcaNeith_kernelTypeExtraction3(kspace, kern);

    interp_kerns = bcaNeith_interpolatorExtraction3(calib, kern_types, kern);

    [res, kspace_interp] = bcaNeith_interpolatekSpace3(kspace, interp_kerns, kern_types, kern);
    % "kspace_interp" variable holds the "interpolated (estimated)" kspace
    % lines where "res" contains the entire filled k-space


    % Removing the padding to keep the original size
    res(1:padsize(1),:, :,:) = [];
    res(:,1:padsize(2),:,:) = [];
    res(:,:,1:padsize(3),:) = [];
    res(end-padsize(1)+1:end, :,:,:) = [];
    res(:,end-padsize(2)+1:end,:,:) = [];
    res(:,:,end-padsize(3)+1:end,:) = [];




end

function res = isKern(kern)
    res = false;
    if length(kern)==3
        if kern(1)>1 && kern(2)>1 && kern(1)>1 
            if nnz(mod(kern-1),2)==0
                res = true;
            end
        end
    end

end
```

Python:
```python
"""Auto-generated from MATLAB source. Review manually before production use."""

from src.fourier3.bcaNeith_interpolatekSpace3 import bcaNeith_interpolatekSpace3
from src.fourier3.bcaNeith_interpolatorExtraction3 import bcaNeith_interpolatorExtraction3
from src.fourier3.bcaNeith_kernelTypeExtraction3 import bcaNeith_kernelTypeExtraction3

import numpy as np

def MATLABGrappa(kspace, calib, kern):
    kern = np.asarray(kern, dtype=int).reshape(-1)
    if not isKern(kern):
        raise ValueError('kern must contain 3 odd values strictly greater than 1')
    padsize = ((kern - 1) // 2).astype(int)
    pad_width = [(int(p), int(p)) for p in padsize[:3].tolist()]
    if np.ndim(kspace) > 3:
        pad_width.extend([(0, 0)] * (np.ndim(kspace) - 3))
    kspace_padded = np.pad(kspace, tuple(pad_width), mode='constant')

    kern_types = bcaNeith_kernelTypeExtraction3(kspace_padded, kern)
    interp_kerns = bcaNeith_interpolatorExtraction3(calib, kern_types, kern)
    res, _kspace_interp = bcaNeith_interpolatekSpace3(kspace_padded, interp_kerns, kern_types, kern)

    xpad, ypad, zpad = (int(padsize[0]), int(padsize[1]), int(padsize[2]))
    xs = slice(xpad, -xpad if xpad else None)
    ys = slice(ypad, -ypad if ypad else None)
    zs = slice(zpad, -zpad if zpad else None)
    return res[xs, ys, zs, ...]


def isKern(kern):
    values = np.asarray(kern, dtype=int).reshape(-1)
    if values.size != 3:
        return False
    if np.any(values <= 1):
        return False
    return bool(np.all(((values - 1) % 2) == 0))


def bcaNeith3(kspace, calib, kern):
    return MATLABGrappa(kspace, calib, kern)
```



## Anti-patterns to reject

- `# TODO(matlab-...)` markers in final code.
- placeholder-only files (`return None`, "not yet implemented") for non-trivial MATLAB sources.
- free-form prose in code output.
