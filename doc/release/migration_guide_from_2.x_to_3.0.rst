:orphan:

*******************************
Migration guide from 2.X to 3.0
*******************************

.. note::
   Much of the work leading to the NetworkX 3.0 release will be included
   in the NetworkX 2.6, 2.7, and 2.8 releases.  For example, we are deprecating a lot
   of old code in these releases.  This guide will discuss this
   ongoing work and will help you understand what changes you can make now
   to minimize the disruption caused by the move to 3.0.

This is a guide for people moving from NetworkX 2.X to NetworkX 3.0.

Any issues with these can be discussed on the `mailing list
<https://groups.google.com/forum/#!forum/networkx-discuss>`_.

The focus of 3.0 release is on addressing years of technical debt, modernizing our codebase,
improving performance, and making it easier to contribute.
We plan to release 3.0 in the summer.

Default dependencies
--------------------

We no longer depend on the "decorator" library, thus NetworkX no longer has
any dependencies.
However, NetworkX 3.0 includes many changes and improvements centered around
tighter integration with other scientific Python libraries; namely
``numpy``, ``scipy``, ``matplotlib``, and ``pandas``.

There are no dependencies for NetworkX's core functionality, such as the data
structures (``Graph``, ``DiGraph``, etc.) and common algorithms, but some
functionality, e.g. functions found in the ``networkx.linalg`` package, are
only available if these additional libraries are installed.

Improved integration with scientific Python
-------------------------------------------

NetworkX 3.0 includes several changes to improve and modernize the usage of
``numpy`` and ``scipy`` within networkx.

- :ref:`Removal of matrix semantics <matrix-to-array>`.

  - Removing all uses of `numpy.matrix` in favor of `numpy.ndarray`.
  - Adoption of the scipy.sparse **array** interface.

- :ref:`NumPy or SciPy implementations of some algorithms by default
  (e.g. pagerank) <scipy-default-impl>`.
- `numpy.random.Generator` support for random number generation.
- :ref:`Replace recarray  support <recarray-to-structured>` with more generic
  support for structured dtypes.

.. _matrix-to-array:

Replacing NumPy/SciPy matrices with arrays
------------------------------------------

The ``numpy.matrix`` has long been discouraged due to significant departures
from the ``ndarray`` interface, namely:

- Matrices are always two-dimensional, leading to different results for common
  operations like indexing and broadcasting.
- The multiplication operator is interpreted as matrix multiplication rather
  than element-wise multiplication.

These differences make code more difficult to understand and often require
boilerplate in order to work with multiple formats.
With the addition of a sparse array interface in scipy version 1.8, NetworkX
3.0 has replaced all instances of scipy sparse matrices and numpy matrices
in favor of their array counterparts.
Any functions that returned either ``scipy.sparse.spmatrix`` or ``numpy.matrix``
objects now return their corresponding array counterparts (``scipy.sparse._sparray``
and ``numpy.ndarray``, respectively) and explicit conversion functions that
resulted in matrix objects have been removed (e.g. ``to_numpy_matrix``).
Users should expect all ``numpy`` and ``scipy.sparse`` objects to obey
*array* semantics in NetworkX 3.X.

.. _scipy-default-impl:

Switch to NumPy/SciPy implementations by default for some algorithms
--------------------------------------------------------------------

Some networkx analysis algorithms can be implemented with very high performance
using linear algebra, such as the ``pagerank`` algorithm.
In NetworkX 2.0, there were multiple implementations of the ``pagerank``
algorithm: ``pagerank`` (a pure-Python implementation), ``pagerank_numpy``
(for dense adjacency matrices), and ``pagerank_scipy`` (sparse adjacency
matrices).
In all practical use-cases, the SciPy implementation vastly outperforms the
others.
In NetworkX 3.0, the `~networkx.algorithms.link_analysis.pagerank_alg.pagerank`
function now uses the SciPy implementation by default.
This means that calling ``nx.pagerank`` now requires SciPy to be installed.
The original Python implementation is still available for pedagogical
purposes as ``networkx.algorithms.link_analysis.pagerank_alg._pagerank_python``
but is not exposed publicly to discourage it's use.
  
Supporting `numpy.random.Generator`
-----------------------------------

NumPy v1.17 introduced a new interface for pseudo-random number generation.
The `~networkx.utils.misc.py_random_state` and `~networkx.utils.misc.np_random_state`
decorators have added support for the new `numpy.random.Generator` instances;
in other words, the ``seed`` argument now accepts `numpy.random.Generator` instances::

    >>> G = nx.barbell_graph(6, 2)
    >>> pos = nx.spring_layout(G, seed=np.random.default_rng(123456789))

The `numpy.random.Generator` interface includes several improvements over the
original `numpy.random.RandomState`, including better statistical properties
and improved performance.
However ``Generator`` is not stream-compatible with ``RandomState`` and
does not guarantee stream-compatibility with future versions of NumPy.
Therefore, the best-practice is to be explicit when using random number
generators.
To guarantee **exact** reproducibility of random numbers across all versions
of NetworkX (past and future), ``RandomState`` is recommended::

    >>> rng = np.random.RandomState(12345)
    >>> pos = nx.spring_layout(G, seed=rng)

For new code where exact stream-reproducibility is less important,
``Generator`` is recommended::

    >>>> rng = np.random.default_rng(12345)
    >>> pos = nx.spring_layout(G, seed=rng)

.. note::  Exact reproducibility of random numbers with ``Generator`` is still
   possible but may require specific versions of numpy to be installed.

.. _recarray-to-structured:

NumPy structured dtypes for multi-attribute adjacency matrices
--------------------------------------------------------------

Prior to NetworkX 3.0, multi-attribute adjacency matrices were supported
through the ``nx.to_numpy_recarray`` conversion function.
`numpy.recarray` is a convenience wrapper around ``ndarray`` with structured
dtypes.
As such, thisconversion function has been removed in NetworkX 3.0 and support
for structured dtypes has been added to ``to_numpy_array`` instead, generally
improving supported for array representations of multi-attribute adjacency::

    >>> import numpy as np
    >>> edges = [
    ...     (0, 1, {"weight": 10, "cost": 2}),
    ...     (1, 2, {"weight": 5, "cost": 100})
    ... ]
    >>> G = nx.Graph(edges)
    >>> # Create an adjacency matrix with "weight" and "cost" attributes
    >>> dtype = np.dtype([("weight", float), ("cost", int)])
    >>> A = nx.to_numpy_array(G, dtype=dtype, weight=None)
    >>> A
    array([[( 0.,   0), (10.,   2), ( 0.,   0)],
           [(10.,   2), ( 0.,   0), ( 5., 100)],
           [( 0.,   0), ( 5., 100), ( 0.,   0)]],
          dtype=[('weight', '<f8'), ('cost', '<i8')])
    >>> A["cost"]
    array([[  0,   2,   0],
           [  2,   0, 100],
           [  0, 100,   0]])
    >>> # The recarray interface can be recovered with ``view``
    >>> A = nx.to_numpy_array(G, dtype=dtype, weight=None).view(np.recarray)
    >>> A
    rec.array([[( 0.,   0), (10.,   2), ( 0.,   0)],
               [(10.,   2), ( 0.,   0), ( 5., 100)],
               [( 0.,   0), ( 5., 100), ( 0.,   0)]],
              dtype=[('weight', '<f8'), ('cost', '<i8')])
    >>> A.weight
    array([[ 0., 10.,  0.],
           [10.,  0.,  5.],
           [ 0.,  5.,  0.]])


Deprecated code
---------------

The functions `read_gpickle` and `write_gpickle` were removed in 3.0.
You can read and write NetworkX graphs as Python pickles.

>>> import pickle
>>> G = nx.path_graph(4)
>>> with open('test.gpickle', 'wb') as f:
...     pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
... 
>>> with open('test.gpickle', 'rb') as f:
...     G = pickle.load(f)
... 

The functions `read_yaml` and `write_yaml` were removed in 3.0.
You can read and write NetworkX graphs in YAML format
using pyyaml.

>>> import yaml
>>> G = nx.path_graph(4)
>>> with open('test.yaml', 'w') as f:
...     yaml.dump(G, f)
... 
>>> with open('test.yaml', 'r') as f:
...     G = yaml.load(f, Loader=yaml.Loader)
