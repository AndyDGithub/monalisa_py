import numpy as np

def DataFromISMRMRD(file_path):
    with h5py.File(file_path, "r") as h5_file:
        raw_data, head, xml_text = _read_dataset_data(h5_file)
    fov, fov_recon = _extract_fov_from_xml(xml_text)
    return {
        "raw_data": raw_data,
        "head": head,
        "xml_text": xml_text,
        "fov": fov,
        "fov_recon": fov_recon
    }
