import numpy as np

def bmCell2Array(c):
    """
    Convert a MATLAB cell array of vectors into a 2-D NumPy array.

    MATLAB reference:
        function a = bmCell2Array(c)
        c_size = size(c);
        c_length = prod(c_size(:));
        c = c(:);
        in_size = size(c{1});
        in_length = prod(in_size(:));
        a_size = [in_length, c_length];

        if isa(c{1}, 'double') & isreal(c{1})
            a = zeros(a_size, 'double');
        elseif isa(c{1}, 'double') & not(isreal(c{1}))
            a = zeros(a_size, 'double');
            a = complex(a, a);
        elseif isa(c{1}, 'single') & isreal(c{1})
            a = zeros(a_size, 'single');
        elseif isa(c{1}, 'single') & not(isreal(c{1}))
            a = zeros(a_size, 'single');
            a = complex(a, a);
        end

        for i = 1:c_length
            temp_a = c{i};
            a(:, i) = temp_a(:);
        end

        a = reshape(a, [in_size, c_size]);
    end
    """

    # Ensure the input is an array of elements
    if isinstance(c, list):
        c = np.array(c, dtype=object)

    c_size = c.shape
    c_length = int(np.prod(c_size))
    c = c.ravel()

    # Get the size of the first element
    first = np.asarray(c[0])
    in_size = first.shape
    in_length = int(np.prod(in_size)) if in_size else 1

    # Determine desired dtype: preserve single/double and complex type
    if np.issubdtype(first.dtype, np.complexfloating):
        if first.dtype == np.complex64:
            desired_dtype = np.complex64
        else:
            desired_dtype = np.complex128
    else:
        desired_dtype = first.dtype

    a = np.zeros((in_length, c_length), dtype=desired_dtype)

    for i in range(c_length):
        temp_a = np.asarray(c[i]).ravel()
        # Cast to the desired dtype if necessary
        if temp_a.dtype != desired_dtype:
            temp_a = temp_a.astype(desired_dtype)
        a[:, i] = temp_a

    return a.reshape(list(in_size) + list(c_size))
