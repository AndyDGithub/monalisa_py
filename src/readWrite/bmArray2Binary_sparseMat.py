def bmArray2Binary_sparseMat(s: Any, argDir: str) -> None:
    """
    Write a ``sparseMat`` structure ``s`` to binary files inside
    ``argDir``.  The behaviour matches the MATLAB reference.

    Parameters
    ----------
    s : object
        The sparse matrix descriptor.  It must provide the
        attributes used in the MATLAB code (``type``,
        ``block_type``, ``kernel_type``, ``r_size``, ``l_size``,
        ``l_nJump``, ``nBlock`` and the data fields that depend
        on the type).
    argDir : str
        Target directory in which the binary files and the header
        text file are created.

    Raises
    ------
    ValueError
        If ``s.type`` is ``'void'`` or if an unsupported sparseMat
        type is encountered.
    """
    # Handle the 'void' case
    if getattr(s, "type", None) == "void":
        raise ValueError("The sparseMat object is of type 'void'.")

    # Ensure output directory exists
    os.makedirs(argDir, exist_ok=True)

    # Build header file path
    my_file = os.path.join(argDir, "bmArray2Binary_sparseMat_header.txt")

    # Extract fields used in the header
    type_string = s.type
    block_type_string = s.block_type
    kernel_type_string = s.kernel_type
    r_size_string = str(s.r_size)
    l_size_string = str(s.l_size)
    l_nJump_string = str(s.l_nJump)

    if s.type in ("matlab_ind", "l_squeezed_matlab_ind"):
        _bmArray2Binary(s.r_nJump, argDir, "r_nJump", "int")
        _bmArray2Binary(s.r_ind, argDir, "r_ind", "int")
        _bmArray2Binary(s.m_val, argDir, "m_val", "single")
        _bmArray2Binary(s.l_ind, argDir, "l_ind", "int")
        _bmArray2Binary(s.N_u, argDir, "N_u", "int")
        _bmArray2Binary(s.d_u, argDir, "d_u", "single")
        _bmArray2Binary(s.nWin, argDir, "nWin", "int")
        _bmArray2Binary(s.kernelParam, argDir, "kernelParam", "single")

        header_lines = [
            type_string,
            block_type_string,
            kernel_type_string,
            r_size_string,
            l_size_string,
            l_nJump_string,
        ]
        _write_header(my_file, header_lines)

    elif s.type in ("cpp_prepared", "l_squeezed_cpp_prepared"):
        _bmArray2Binary(s.r_nJump, argDir, "r_nJump", "int")
        _bmArray2Binary(s.r_jump, argDir, "r_jump", "int")
        _bmArray2Binary(s.m_val, argDir, "m_val", "single")
        _bmArray2Binary(s.l_jump, argDir, "l_jump", "int")
        _bmArray2Binary(s.N_u, argDir, "N_u", "int")
        _bmArray2Binary(s.d_u, argDir, "d_u", "single")
        _bmArray2Binary(s.nWin, argDir, "nWin", "int")
        _bmArray2Binary(s.kernelParam, argDir, "kernelParam", "single")

        _bmArray2Binary(s.block_length, argDir, "block_length", "int")
        _bmArray2Binary(s.l_block_start, argDir, "l_block_start", "int")
        _bmArray2Binary(s.m_block_start, argDir, "m_block_start", "int64")

        header_lines = [
            type_string,
            block_type_string,
            kernel_type_string,
            r_size_string,
            l_size_string,
            l_nJump_string,
            str(s.nBlock),
        ]
        _write_header(my_file, header_lines)

    else:
        raise ValueError(f"Unsupported sparseMat type: {s.type}")
