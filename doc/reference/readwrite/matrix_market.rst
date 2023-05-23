*************
Matrix Market
*************

The `Matrix Market`_ exchange format is a text-based file format described by
NIST.
Matrix Market supports both a **coordinate format** for sparse matrices and
an **array format** for dense matrices.
The :mod:`scipy.io` module provides the `scipy.io.mmread` and `scipy.io.mmwrite`
functions to read and write data in Matrix Market format, respectively.
These functions work with either `numpy.ndarray` or `scipy.sparse.coo_matrix`
objects depending on whether the data is in **array** or **coordinate** format.
These functions can be combined with those of NetworkX's `~networkx.convert_matrix`
module to read and write Graphs in Matrix Market format.

.. _Matrix Market: https://math.nist.gov/MatrixMarket/formats.html

Examples
========

Reading and writing graphs using Matrix Market's **array format** for dense
matrices::

    >>> import scipy as sp
    >>> import io  # Use BytesIO as a stand-in for a Python file object
    >>> fh = io.BytesIO()

    >>> G = nx.complete_graph(5)
    >>> a = nx.to_numpy_array(G)
    >>> print(a)
    [[0. 1. 1. 1. 1.]
     [1. 0. 1. 1. 1.]
     [1. 1. 0. 1. 1.]
     [1. 1. 1. 0. 1.]
     [1. 1. 1. 1. 0.]]

    >>> # Write to file in Matrix Market array format
    >>> sp.io.mmwrite(fh, a)
    >>> print(fh.getvalue().decode('utf-8'))  # file contents
    %%MatrixMarket matrix array real symmetric
    %
    5 5
    0.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    0.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    0.0000000000000000e+00
    1.0000000000000000e+00
    1.0000000000000000e+00
    0.0000000000000000e+00
    1.0000000000000000e+00
    0.0000000000000000e+00

    >>> # Read from file
    >>> fh.seek(0)
    >>> H = nx.from_numpy_array(sp.io.mmread(fh))
    >>> H.edges() == G.edges()
    True

Reading and writing graphs using Matrix Market's **coordinate format** for
sparse matrices::

    >>> import scipy as sp
    >>> import io  # Use BytesIO as a stand-in for a Python file object
    >>> fh = io.BytesIO()

    >>> G = nx.path_graph(5)
    >>> m = nx.to_scipy_sparse_array(G)
    >>> print(m)
      (0, 1)        1
      (1, 0)        1
      (1, 2)        1
      (2, 1)        1
      (2, 3)        1
      (3, 2)        1
      (3, 4)        1
      (4, 3)        1

    >>> sp.io.mmwrite(fh, m)
    >>> print(fh.getvalue().decode('utf-8'))  # file contents
    %%MatrixMarket matrix coordinate integer symmetric
    %
    5 5 4
    2 1 1
    3 2 1
    4 3 1
    5 4 1

    >>> # Read from file
    >>> fh.seek(0)
    >>> H = nx.from_scipy_sparse_array(sp.io.mmread(fh))
    >>> H.edges() == G.edges()
    True
