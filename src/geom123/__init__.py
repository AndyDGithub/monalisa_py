"""
Compatibility exports for legacy imports such as:
    from src.geom123 import bmTraj
"""

from src.trajN.bmTraj import bmTraj

__all__ = ["bmTraj"]
