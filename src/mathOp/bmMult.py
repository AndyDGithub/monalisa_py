import numpy as np

def bmMult(x, y):
    """
    % Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023

    function out = bmMult(x, y)

    if iscell(x) & iscell(y)
    
        N = size(x(:), 1) ;
        out = cell(size(x));
        
        for i = 1:N
            out{i} = x{i} .* y{i};
        end
        
    elseif ~iscell(x) & iscell(y)
    
        N = size(y(:), 1) ;
        out = cell(size(y));
        
        for i = 1:N
            out{i} = x.*y{i};
        end
        
    elseif ~iscell(x) & ~iscell(y)
        out = x .* y;
    end

    end
    """
    # Handle MATLAB cell arrays (Python lists)
    if isinstance(x, list) and isinstance(y, list):
        # Element-wise multiplication for list of elements
        return [bmMult(xi, yi) for xi, yi in zip(x, y)]
    elif isinstance(x, list) and not isinstance(y, list):
        # Scalar y times each element of x
        return [xi * y for xi in x]
    elif not isinstance(x, list) and isinstance(y, list):
        # Scalar x times each element of y
        return [x * yi for yi in y]
    else:
        # Both are non-cell (numpy arrays, scalars, or other types)
        try:
            return np.multiply(x, y)
        except Exception:
            return x * y
