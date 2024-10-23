import numpy as np

def handle_numpy_scalar(value):
    """
    Function to handle numpy scalars and convert them to Python native types if needed.
    """
    # Check if the value is a numpy scalar
    if np.isscalar(value):
        print(f"Input is a numpy scalar of type: {type(value)}")

        # Convert the numpy scalar to a native Python type (e.g., int, float)
        if isinstance(value, (np.integer, np.int_)):
            return int(value)
        elif isinstance(value, (np.floating, np.float_)):
            return float(value)
        else:
            return value
    else:
        print("Input is not a numpy scalar.")
        return value

# Example usage
if __name__ == "__main__":
    # Numpy scalar examples
    np_int = np.int32(10)
    np_float = np.float64(10.5)

    # Handling numpy scalars
    python_int = handle_numpy_scalar(np_int)
    python_float = handle_numpy_scalar(np_float)

    print(f"Converted numpy int to python int: {python_int}, type: {type(python_int)}")
    print(f"Converted numpy float to python float: {python_float}, type: {type(python_float)}")
