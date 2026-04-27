import numpy as np
from src.varargin.bmVarargin import bmVarargin

def bmGetNat(varargin):
    # Extract optional arguments
    prompt = bmVarargin(varargin)

    # Set default value
    if not prompt or (not isinstance(prompt, str) and not isinstance(prompt, bytes)):
        prompt = 'Enter a natural number : '

    # Prompt user for input
    myAnswer = input(f'{prompt} ')

    # Test if input is valid
    try:
        myAnswer = int(myAnswer)
        out = np.fix(np.abs(myAnswer))
    except ValueError:
        out = 0

    return out
