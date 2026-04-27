from third_part.matlab_compat.matlab_native import num2str, disp

def t(varargin):
    N = len(varargin) // 3
    s = []
    count = 0
    # Process inputs
    for _ in range(N):
        x = varargin[count]
        count += 1
        y = varargin[count]
        count += 1
        z = varargin[count]
        s.append(num2str(round(x / y * 100)) + '% of ' + z + '   ')
    disp(' '.join(s))
    return bmDispPercent

def bmDispPercent(varargin):
    return t(varargin)
