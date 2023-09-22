Deprecations
============

.. _deprecation_policy:

Policy
------

If the behavior of the library has to be changed, a deprecation cycle must be
followed to warn users.

A deprecation cycle is *not* necessary when:

* adding a new function, or
* adding a new keyword argument to the *end* of a function signature, or
* fixing buggy behavior

A deprecation cycle is necessary for *any breaking API change*, meaning a
change where the function, invoked with the same arguments, would return a
different result after the change. This includes:

* changing the order of arguments or keyword arguments, or
* adding arguments or keyword arguments to a function, or
* changing the name of a function, class, method, etc., or
* moving a function, class, etc. to a different module, or
* changing the default value of a function's arguments.

Usually, our policy is to put in place a deprecation cycle over two minor
releases (e.g., if a deprecation warning appears in 2.3, then the functionality
should be removed in 2.5).  For major releases we usually require that all
deprecations have at least a 1-release deprecation cycle (e.g., if 3.0 occurs
after 2.5, then all removed functionality in 3.0 should be deprecated in 2.5).

Note that these 1- and 2-release deprecation cycles for major and minor
releases is not a strict rule and in some cases, the developers can agree on a
different procedure upon justification (like when we can't detect the change,
or it involves moving or deleting an entire function for example).

Todo
----

Make sure to review ``networkx/conftest.py`` after removing deprecated code.

Version 3.0
~~~~~~~~~~~

* In ``readwrite/gml.py`` remove ``literal_stringizer`` and related tests.
* In ``readwrite/gml.py`` remove ``literal_destringizer`` and related tests.
* Remove ``copy`` method in the coreview Filtered-related classes and related tests.
* In ``algorithms/link_analysis/pagerank_alg.py`` replace ``pagerank`` with ``pagerank_scipy``.
* In ``algorithms/link_analysis/pagerank_alg.py`` rename ``pagerank_numpy`` as ``_pagerank_numpy``.
* In ``convert_matrix.py`` remove ``order`` kwarg from ``to_pandas_edgelist`` and docstring
* In ``algorithms/operators/binary.py`` remove ``name`` kwarg from ``union`` and docstring.
* In ``algorithms/link_analysis/pagerank_alg.py``, remove the
  ``np.asmatrix`` wrappers on the return values of ``google_matrix`` and remove
  the associated FutureWarning.
* In ``linalg/attrmatrix.py`` remove the FutureWarning, update the
  return type by removing ``np.asmatrix``, and update the docstring to
  reflect that the function returns a ``numpy.ndarray`` instance.
* In ``algorithms/distance_measures.py`` remove ``extrema_bounding``.
* In ``algorithms/matching.py``, remove parameter ``maxcardinality`` from ``min_weight_matching``.


Version 3.2
~~~~~~~~~~~
* In ``generators/directed.py`` remove the ``create_using`` keyword argument
  for the ``scale_free_graph`` function.
* Remove pydot functionality ``drawing/nx_pydot.py``, if pydot is still not being maintained. See #5723
* Remove renamed function ``join()`` in ``algorithms/tree/operations.py`` and
  in ``doc/reference/algorithms/trees.rst``

Version 3.3
~~~~~~~~~~~
* Remove the ``forest_str`` function from ``readwrite/text.py``. Replace
  existing usages with ``write_network_text``.
* Change ``single_target_shortest_path_length`` in ``algorithms/shortest_path/unweighted.py``
  to return a dict. See #6527
* Change ``shortest_path`` in ``algorithms/shortest_path/generic.py``
  to return a iterator. See #6527

Version 3.4
~~~~~~~~~~~
* Remove the ``sort_neighbors`` input parameter from ``generic_bfs_edges``.
* Remove ``MultiDiGraph_EdgeKey`` class from ``algorithms/tree/branchings.py``. 
* Remove ``Edmonds`` class from ``algorithms/tree/branchings.py``.
* Remove ``normalized`` kwarg from ``algorithms.s_metric``
