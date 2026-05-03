from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

from third_part.twix_for_monalisa.mapVBVD_JH_for_monalisa import mapVBVD_JH_for_monalisa
from src.fourierN.bmIDF import bmIDF


def bmTwix_info(myArg) -> None:
    """Print information from a Siemens raw-data Twix object and display a
    magnitude-spectrum figure.

    Authors:
        Bastien Milani
        CHUV and UNIL
        Lausanne - Switzerland
        May 2023

    Parameters
    ----------
    myArg : str or twix object
        Either the path to the Siemens raw data file or a Twix object
        (as returned by ``mapVBVD_JH_for_monalisa``).
    """
    if isinstance(myArg, str):
        myTwix = mapVBVD_JH_for_monalisa(myArg)
        if isinstance(myTwix, list):
            myTwix = myTwix[-1]
    else:
        myTwix = myArg

    N = None
    nShot = None
    nLine = None
    nSeg = None
    nPar = None
    nCh = None
    nEcho = None

    hdr_Meas_ReadFoV = None
    hdr_Meas_FOV = None

    hdr_Config_ReadFoV = None
    hdr_Config_PhaseFoV = None
    hdr_Config_PeFOV = None
    hdr_Config_RoFOV = None

    hdr_Dicom_dPhaseFOV = None
    hdr_Dicom_dReadoutFOV = None

    hdr_Protocol_ReadFoV = None
    hdr_Protocol_PeFOV = None
    hdr_Protocol_PhaseFoV = None

    N = myTwix.image.NCol
    nShot = myTwix.image.NSeg
    nLine = myTwix.image.NLin
    nSeg = nLine // nShot
    nPar = myTwix.image.NPar
    nEcho = myTwix.image.NEco

    hdr = myTwix.hdr

    if hasattr(hdr, 'Meas'):
        meas = hdr.Meas
        if hasattr(meas, 'ReadFoV'):
            hdr_Meas_ReadFoV = meas.ReadFoV * 2
        if hasattr(meas, 'FOV'):
            hdr_Meas_FOV = meas.FOV * 2
    elif isinstance(hdr, dict) and 'Meas' in hdr:
        meas = hdr['Meas']
        if 'ReadFoV' in meas:
            hdr_Meas_ReadFoV = meas['ReadFoV'] * 2
        if 'FOV' in meas:
            hdr_Meas_FOV = meas['FOV'] * 2

    if hasattr(hdr, 'Config'):
        cfg = hdr.Config
        if hasattr(cfg, 'ReadFoV'):
            hdr_Config_ReadFoV = cfg.ReadFoV * 2
        if hasattr(cfg, 'PhaseFoV'):
            hdr_Config_PhaseFoV = cfg.PhaseFoV * 2
        if hasattr(cfg, 'PeFOV'):
            hdr_Config_PeFOV = cfg.PeFOV * 2
        if hasattr(cfg, 'RoFOV'):
            hdr_Config_RoFOV = cfg.RoFOV * 2
    elif isinstance(hdr, dict) and 'Config' in hdr:
        cfg = hdr['Config']
        if 'ReadFoV' in cfg:
            hdr_Config_ReadFoV = cfg['ReadFoV'] * 2
        if 'PhaseFoV' in cfg:
            hdr_Config_PhaseFoV = cfg['PhaseFoV'] * 2
        if 'PeFOV' in cfg:
            hdr_Config_PeFOV = cfg['PeFOV'] * 2
        if 'RoFOV' in cfg:
            hdr_Config_RoFOV = cfg['RoFOV'] * 2

    if hasattr(hdr, 'Dicom'):
        dcm = hdr.Dicom
        if hasattr(dcm, 'dPhaseFOV'):
            hdr_Dicom_dPhaseFOV = dcm.dPhaseFOV * 2
        if hasattr(dcm, 'dReadoutFOV'):
            hdr_Dicom_dReadoutFOV = dcm.dReadoutFOV * 2
    elif isinstance(hdr, dict) and 'Dicom' in hdr:
        dcm = hdr['Dicom']
        if 'dPhaseFOV' in dcm:
            hdr_Dicom_dPhaseFOV = dcm['dPhaseFOV'] * 2
        if 'dReadoutFOV' in dcm:
            hdr_Dicom_dReadoutFOV = dcm['dReadoutFOV'] * 2

    if hasattr(hdr, 'Protocol'):
        prot = hdr.Protocol
        if hasattr(prot, 'ReadFoV'):
            hdr_Protocol_ReadFoV = prot.ReadFoV * 2
        if hasattr(prot, 'PeFOV'):
            hdr_Protocol_PeFOV = prot.PeFOV * 2
        if hasattr(prot, 'PhaseFoV'):
            hdr_Protocol_PhaseFoV = prot.PhaseFoV * 2
    elif isinstance(hdr, dict) and 'Protocol' in hdr:
        prot = hdr['Protocol']
        if 'ReadFoV' in prot:
            hdr_Protocol_ReadFoV = prot['ReadFoV'] * 2
        if 'PeFOV' in prot:
            hdr_Protocol_PeFOV = prot['PeFOV'] * 2
        if 'PhaseFoV' in prot:
            hdr_Protocol_PhaseFoV = prot['PhaseFoV'] * 2

    y_raw = myTwix.image.unsorted()
    y_raw = np.transpose(y_raw, (1, 0, 2))
    y_raw_shape = np.array(y_raw.shape, dtype=int)
    nCh = int(y_raw_shape[0])
    y_raw = y_raw.reshape((nCh, N, nSeg, nShot))

    mySI = np.squeeze(y_raw[:, :, 0, :])
    mySI = bmIDF(mySI, nDim=1, NZero=0, gridType=None)
    mySI = np.squeeze(np.sqrt(np.sum(np.abs(mySI) ** 2, axis=0)))
    mySI = mySI - mySI.min()
    if mySI.max() > 0:
        mySI = mySI / mySI.max()

    mySize_1 = mySI.shape[0]
    mySize_2 = mySI.shape[1]
    x_SI = np.arange(1, mySize_1 + 1, dtype=float).reshape(-1, 1)
    x_SI = np.tile(x_SI, (1, mySize_2))

    s_mean = np.mean(x_SI * mySI, axis=0)
    s_center_mass = np.sum(x_SI * mySI, axis=0) / np.sum(mySI, axis=0)

    window_size = 10
    threshold = float(np.std(s_mean)) * 0.1

    n = len(s_mean)
    running_std = np.full(n, np.nan)
    half = window_size // 2
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        running_std[i] = float(np.std(s_mean[lo:hi], ddof=0))

    shotOff_arr = np.where(running_std < threshold)[0]
    shotOff = int(shotOff_arr[0]) + 1 if len(shotOff_arr) > 0 else None

    def _fmt(val):
        return f"{val}" if val is not None else "empty"

    print()
    print(f"N     = {_fmt(N)}")
    print(f"nSeg  = {_fmt(nSeg)}")
    print(f"nShot = {_fmt(nShot)}")
    print(f"nLine = {_fmt(nLine)}")
    print(f"nPar  = {_fmt(nPar)}")
    print(f"nCh   = {_fmt(nCh)}")
    print(f"nEcho = {_fmt(nEcho)}")
    print()

    def _fov_line(label, val):
        if val is None:
            print(f"{label} is empty.")
        else:
            print(f"{label} = {val:.2f}")

    _fov_line("hdr_Meas_ReadFoV      ", hdr_Meas_ReadFoV)
    _fov_line("hdr_Meas_FOV          ", hdr_Meas_FOV)
    print()
    _fov_line("hdr_Config_ReadFoV    ", hdr_Config_ReadFoV)
    _fov_line("hdr_Config_PhaseFoV   ", hdr_Config_PhaseFoV)
    _fov_line("hdr_Config_PeFOV      ", hdr_Config_PeFOV)
    _fov_line("hdr_Config_RoFOV      ", hdr_Config_RoFOV)
    print()
    _fov_line("hdr_Dicom_dPhaseFOV   ", hdr_Dicom_dPhaseFOV)
    _fov_line("hdr_Dicom_dReadoutFOV ", hdr_Dicom_dReadoutFOV)
    print()
    _fov_line("hdr_Protocol_ReadFoV  ", hdr_Protocol_ReadFoV)
    _fov_line("hdr_Protocol_PeFOV    ", hdr_Protocol_PeFOV)
    _fov_line("hdr_Protocol_PhaseFoV ", hdr_Protocol_PhaseFoV)
    print()

    if shotOff is not None:
        print(f"Steady state reached at shot {shotOff}")
    else:
        print("Steady state not reached within the data range.")
    print()

    fig, ax = plt.subplots(num="TwixInfo Magnitude")
    cmax = float(3.0 * np.mean(mySI))
    im = ax.imshow(
        mySI,
        aspect="auto",
        origin="lower",
        vmin=0.0,
        vmax=cmax,
        cmap="gray",
    )
    fig.colorbar(im, ax=ax)

    shots = np.arange(1, mySize_2 + 1)
    ax.plot(shots - 1, s_center_mass, "g.-", label="Center of Mass")
    ax.plot(shots - 1, s_mean, "r.-", label="Mean")

    if shotOff is not None:
        ax.axvline(x=shotOff - 1, color="c", linestyle="--", label="Steady State")
        ax.text(
            shotOff - 1 + 5,
            int(N * 0.75),
            f"shot = {shotOff}",
            ha="left",
            color="black",
            bbox={"facecolor": "white", "pad": 0.5},
        )

    ax.legend(loc="best")
    ax.set_xlabel("nShot")
    ax.set_ylabel("N", rotation=0)
    ax.set_title(
        "Magnitude spectrum for first segment of each shot\n"
        "(estimates which shots should be excluded)"
    )
    plt.show()
