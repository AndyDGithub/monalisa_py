from src.varargin.bmVarargin import bmVarargin
import numpy as np

def bmGetNum(varargin):
    # Extract optional arguments
    prompt = bmVarargin(varargin)
    
    # Set default value
    if not isinstance(prompt, (str, bytes)):
        prompt = "Enter a number : "
    
    # Prompt user for input
    myAnswer = input(f"{prompt} ")
    
    # Test if input is valid
    if not myAnswer:
        return 0

    # Turn answer to number
    try:
        myAnswer = np.array([np.float64(x) for x in myAnswer.split(',')])
    except ValueError:
        return 0

    # Return valid answer (0 otherwise)
    return myAnswer
