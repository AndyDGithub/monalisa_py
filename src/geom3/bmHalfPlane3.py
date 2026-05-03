import numpy as np

def bmHalfPlane3(argPlane, N_u):
    """
    Strict deterministic baseline port from MATLAB.
    
    Args:
        argPlane: A dictionary containing the parameters of the plane.
            - .p: A vector representing a point on the plane.
            - .n: A vector representing the normal to the plane.
        N_u: A tuple specifying the dimensions of the grid over which the p
plane is evaluated.
    
    Returns:
        m: A 2D array indicating whether points are above or below the plan
plane.
    """
    # Unpack the plane parameters
    p = argPlane['p']
    n = argPlane['n']
    
    # Create a grid of coordinates
    X, Y, Z = np.meshgrid(np.arange(1, N_u[0] + 1), 
                           np.arange(1, N_u[1] + 1), 
                           np.arange(1, N_u[2] + 1))
    
    # Flatten the grid to vectors
    x = np.stack((X.flatten(), Y.flatten(), Z.flatten()), axis=1)
    
    # Translate points so that p is at the origin
    x -= p
    
    # Calculate the projection of each point onto the normal vector
    projections = np.sum(x * n, axis=1) > 0
    
    # Reshape the results to match N_u dimensions
    m = projections.reshape(N_u)
    
    return m
