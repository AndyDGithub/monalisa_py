# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmNumList(argNum):
    """
    Generate a list of zero-padded string indices from 0 to argNum-1.
    The padding width matches the number of digits of argNum-1.
    """
    n = int(argNum)
    if n <= 0:
        raise ValueError("argNum must be a positive integer")
    max_val = n - 1
    width = len(str(max_val))
    return [str(i).zfill(width) for i in range(n)]
