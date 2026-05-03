import numpy as np

# MATLAB original:
# function s = bmConv1(f, h, dx)
#     f = f(:).';
#     h = h(:).';
#     N = size(f(:), 1);
#     s = zeros(1, N);
#     for n = -N/2:N/2-1
#         temp_sum = 0;
#         for k = -N/2:N/2-1
#             ind_2 = k + N/2 + 1;
#             ind_3 = private_mod(n-k, N) + N/2 + 1;
#             temp_sum = temp_sum + dx*f(1, ind_2)*h(1, ind_3);
#         end
#         s(n + N/2 + 1) = temp_sum;
#     end
# end
#
# function myMod = private_mod(n, N)
#     myMod = mod(n + N/2, N) - N/2;
# end

def bmConv1(f, h, dx):
    """
    Convolution of two 1-D sequences using a circular shift, matching the M
MATLAB
    implementation of bmConv1.  The function assumes *f* and *h* are 1-D ar
array
    like objects; the length of the output is the same as the input length.
length.
    """
    f = np.asarray(f).ravel()
    h = np.asarray(h).ravel()
    N = f.size
    s = np.empty(N, dtype=np.result_type(f, h, dx))

    for n in range(-N // 2, N // 2):
        temp_sum = 0.0
        for k in range(-N // 2, N // 2):
            ind_2 = k + N // 2                 # 0-based index
            ind_3 = private_mod(n - k, N) + N // 2
            temp_sum += dx * f[ind_2] * h[ind_3]
        s[n + N // 2] = temp_sum

    return s


def private_mod(n, N):
    """
    Return the MATLAB-like modulus of *n* with respect to *N*, shifted to t
the
    range [-N/2, N/2-1] for even *N*.
    """
    return (n + N // 2) % N - N // 2
