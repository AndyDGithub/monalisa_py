import os
def bmMitosius_nCell(mitosius_dir):
    nCell = 0
    try:
        for entry in os.listdir(mitosius_dir):
            full_path = os.path.join(mitosius_dir, entry)
            if os.path.isdir(full_path):
                if len(entry) >= 5 and entry.startswith('cell_'):
                    nCell += 1
    except Exception:
        nCell = None
    return nCell
