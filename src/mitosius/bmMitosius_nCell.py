import os

def bmMitosius_nCell(mitosius_dir: str) -> int:
    """
    Count the number of subfolders in `mitosius_dir` whose names begin with
with 'cell_'.

    Parameters
    ----------
    mitosius_dir : str
        Path to the directory containing the cell folders.

    Returns
    -------
    int
        Number of folders starting with ``cell_``. An exception is raised
        if the directory does not exist or is inaccessible, mirroring MATLA
MATLAB's
        behaviour.
    """
    count = 0
    for entry in os.listdir(mitosius_dir):
        full_path = os.path.join(mitosius_dir, entry)
        if os.path.isdir(full_path) and entry.startswith("cell_"):
            count += 1
    return count
