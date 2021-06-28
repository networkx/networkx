**************************
Matrix Market Graph Format
**************************

The `Matrix Market`_ exchange format is a ASCII-encoded text-based file format
described by Nist.
Matrix Market supports both a **coordinate format** for sparse matrices and
an **array format** for dense matrices.
The :mod:`scipy.io` module provides the `scipy.io.mmread` and `scipy.io.mmwrite`
functions to read and write data in Matrix Market format, respectively.
These functions work with either `numpy.ndarray` or `scipy.sparse.coo_matrix`
objects depending on whether the data is in **array** or **coordinate** format.
These functions can be combined with those of NetworkX's :mod:`convert_matrix`
module to read and write Graphs in Matrix Market format.

.. _Matrix Market: https://math.nist.gov/MatrixMarket/formats.html
