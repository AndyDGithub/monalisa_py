import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape


def bmVolumeElement(argTraj, argType, *varargin):
    # Cell-array case: compute per element
    if isinstance(argTraj, (list, tuple)) or (
        isinstance(argTraj, np.ndarray) and argTraj.dtype == object
    ):
        return [bmVolumeElement(tj, argType, *varargin) for tj in argTraj]

    t = bmPointReshape(argTraj)

    N_u = varargin[0] if len(varargin) > 0 else None
    dK_u = varargin[1] if len(varargin) > 1 else None

    if argType == 'voronoi_box2':
        from src.geom2.bmVolumeElement_voronoi_box2 import bmVolumeElement_voronoi_box2
        from src.traj123.bmTraj_formatTraj import bmTraj_formatTraj
        formatedTraj, _, formatedIndex, formatedWeight = bmTraj_formatTraj(t)
        v = bmVolumeElement_voronoi_box2(formatedTraj, N_u, dK_u)
        v = v.ravel()
        v = v[formatedIndex.ravel()] * formatedWeight.ravel()

    elif argType == 'voronoi_box3':
        from src.geom3.bmVolumeElement_voronoi_box3 import bmVolumeElement_voronoi_box3
        from src.traj123.bmTraj_formatTraj import bmTraj_formatTraj
        formatedTraj, _, formatedIndex, formatedWeight = bmTraj_formatTraj(t)
        v = bmVolumeElement_voronoi_box3(formatedTraj, N_u, dK_u)
        v = v.ravel()
        v = v[formatedIndex.ravel()] * formatedWeight.ravel()

    elif argType == 'voronoi_center_out_radial2':
        from src.geom2.bmVolumeElement_voronoi_center_out_radial2 import bmVolumeElement_voronoi_center_out_radial2
        v = bmVolumeElement_voronoi_center_out_radial2(t)

    elif argType == 'voronoi_center_out_radial3':
        from src.geom3.bmVolumeElement_voronoi_center_out_radial3 import bmVolumeElement_voronoi_center_out_radial3
        v = bmVolumeElement_voronoi_center_out_radial3(t)

    elif argType == 'voronoi_full_radial2':
        from src.geom2.bmVolumeElement_voronoi_full_radial2 import bmVolumeElement_voronoi_full_radial2
        v = bmVolumeElement_voronoi_full_radial2(t)

    elif argType == 'voronoi_full_radial3':
        from src.geom3.bmVolumeElement_voronoi_full_radial3 import bmVolumeElement_voronoi_full_radial3
        v = bmVolumeElement_voronoi_full_radial3(t)

    elif argType == 'voronoi_full_radial2_nonUnique':
        from src.geom2.bmVolumeElement_voronoi_full_radial2_nonUnique import bmVolumeElement_voronoi_full_radial2_nonUnique
        nAverage = varargin[0] if varargin else 1
        v = bmVolumeElement_voronoi_full_radial2_nonUnique(t, nAverage)

    elif argType == 'voronoi_full_radial3_nonUnique':
        from src.geom3.bmVolumeElement_voronoi_full_radial3_nonUnique import bmVolumeElement_voronoi_full_radial3_nonUnique
        v = bmVolumeElement_voronoi_full_radial3_nonUnique(t)

    elif argType == 'imDeformField2':
        from src.geom2.bmVolumeElement_imDeformField2 import bmVolumeElement_imDeformField2
        v = bmVolumeElement_imDeformField2(t, N_u)

    elif argType == 'imDeformField3':
        from src.geom3.bmVolumeElement_imDeformField3 import bmVolumeElement_imDeformField3
        v = bmVolumeElement_imDeformField3(t, N_u)

    elif argType == 'cartesian2':
        from src.geom2.bmVolumeElement_cartesian2 import bmVolumeElement_cartesian2
        v = bmVolumeElement_cartesian2(t)

    elif argType == 'cartesian3':
        from src.geom3.bmVolumeElement_cartesian3 import bmVolumeElement_cartesian3
        v = bmVolumeElement_cartesian3(t)

    elif argType == 'randomPartialCartesian2_x':
        from src.geom2.bmVolumeElement_randomPartialCartesian2_x import bmVolumeElement_randomPartialCartesian2_x
        v = bmVolumeElement_randomPartialCartesian2_x(t, N_u, dK_u)

    elif argType == 'randomPartialCartesian3_x':
        from src.geom3.bmVolumeElement_randomPartialCartesian3_x import bmVolumeElement_randomPartialCartesian3_x
        v = bmVolumeElement_randomPartialCartesian3_x(t, N_u, dK_u)

    elif argType == 'full_radial3':
        from src.geom3.bmVolumeElement_full_radial3 import bmVolumeElement_full_radial3
        v = bmVolumeElement_full_radial3(t)

    elif argType == 'center_out_radial3':
        from src.geom3.bmVolumeElement_center_out_radial3 import bmVolumeElement_center_out_radial3
        v = bmVolumeElement_center_out_radial3(t)

    else:
        raise ValueError(
            f'bmVolumeElement: unknown trajectory type "{argType}". '
            'Check the possible inputs or implement a custom volume element function.'
        )

    v = np.asarray(v)
    if np.any(np.isnan(v)):
        print('Warning: There are NaNs in the volume elements! You need to replace them.')

    return v
