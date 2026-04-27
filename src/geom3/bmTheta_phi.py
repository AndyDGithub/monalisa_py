import numpy as np
from scipy import signal

def bmTheta_phi(n):
    """Auto-generated from MATLAB source. Review manually before production use."""

    # [theta, phi] = bmTheta_phi(n)
    #
    # This function calculates the spherical coordinates describing the given
    # the vector n.
    #
    # Authors:
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    #
    # Contributors:
    # Dominik Helbing (Documentation & Comments)
    # MattechLab 2024
    #
    # Parameters:
    # n (list): The vector of which the spherical coordinates should be calculated.
    #
    # Returns:
    # theta (double): Polar angle between n and the Z-axis (3rd axis). Describes the tilt away from the Z-axis.
    # phi (double): Azimuthal angle describing the orientation of n in the XY-plane.
    #
    # Notes:
    # This function can be used to calculate the yaw and pitch Euler angles of a rotation. The calculation only works if the applied rotation is a rotation of a plane around the rotation axis n or the rotation matrix is calculated using proper Euler angles and a matrix multiplication of Z(phi)Y(theta)Z(psi), where Y and Z are the rotation matrices around
    # the respectve axis.
    #
    # n = [sin(theta)cos(phi), sin(theta)sin(phi), cos(theta)]' in spherical coordinates.
    # For floating point error
    myEps = np.finfo(float).eps
    # Have n as a column vector and ensure unit length of 1
    n = np.reshape(n, (3, 1))
    n = n / np.linalg.norm(n)
    # Calculate the polar angle from the third element
    theta = np.arccos(n[2])
    # Check for Gimbal lock condition (n = [0;0;1])
    if abs(1 - n[2]) > myEps:
        sin_theta = np.sqrt(n[0]**2 + n[1]**2)
        cos_phi = n[0] / sin_theta
        sin_phi = n[1] / sin_theta
        norm_phi = np.sqrt(cos_phi**2 + sin_phi**2)
        cos_phi /= norm_phi
        sin_phi /= norm_phi
        phi = np.angle(complex(cos_phi, sin_phi))
    else:
        phi = 0

    return (theta.item(), phi.item())
