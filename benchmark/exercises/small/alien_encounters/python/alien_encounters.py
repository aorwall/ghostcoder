def resize_matrix(matrix, length):
    # Copy the matrix to avoid modifying the original
    matrix_copy = matrix.copy()

    # If the matrix is too long, remove rows from the end
    if len(matrix_copy) > length:
        matrix_copy = matrix_copy[:length]
    # If the matrix is too short, add rows filled with zeros at the end
    elif len(matrix_copy) < length:
        # Special case: if the matrix is empty, assume it should have one column
        num_columns = len(matrix_copy[0]) if matrix_copy else 1
        while len(matrix_copy) < length:
            matrix_copy.append([0]*num_columns)

    return matrix_copy