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
* In ``utils/misc.py`` remove ``is_string_like`` and related tests.
* In ``utils/misc.py`` remove ``make_str`` and related tests.
* In ``utils/misc.py`` remove ``is_iterator``.
* In ``utils/misc.py`` remove ``iterable``.
* In ``utils/misc.py`` remove ``is_list_of_ints``.
* In ``utils/misc.py`` remove ``consume``.
* In ``utils/misc.py`` remove ``default_opener``.
* In ``utils/misc.py`` remove ``empty_generator``.
* Remove ``utils/contextmanagers.py`` and related tests.
* In ``linalg/algebraicconnectivity.py`` remove ``_CholeskySolver`` and related code.
* In ``readwrite/json_graph/cytoscape.py``, change function signature for
  ``cytoscape_graph`` and ``cytoscape_data`` to replace the ``attrs`` keyword.
  argument with explicit ``name`` and ``ident`` keyword args.
* In ``readwrite/json_graph/tree.py``, remove ``attrs`` kwarg from ``tree_graph``
  and ``tree_data``.
* Remove ``copy`` method in the coreview Filtered-related classes and related tests.
* In ``algorithms/link_analysis/pagerank_alg.py`` replace ``pagerank`` with ``pagerank_scipy``.
* In ``algorithms/link_analysis/pagerank_alg.py`` rename ``pagerank_numpy`` as ``_pagerank_numpy``.
* In ``convert_matrix.py`` remove ``order`` kwarg from ``to_pandas_edgelist`` and docstring
* In ``algorithms/link_analysis/hits_alg.py`` remove ``hub_matrix`` and ``authority_matrix``
* In ``algorithms/link_analysis/hits_alg.py``, remove ``hits_numpy`` and ``hist_scipy``.
* Remove ``testing``.
* In ``linalg/graphmatrix.py`` remove ``adj_matrix``.
* In ``algorithms/operators/binary.py`` remove ``name`` kwarg from ``union`` and docstring.
* In ``generators/geometric.py`` remove ``euclidean`` and tests.
* In ``algorithms/link_analysis/pagerank_alg.py``, remove the
  ``np.asmatrix`` wrappers on the return values of ``google_matrix`` and remove
  the associated FutureWarning.
* In ``linalg/attrmatrix.py`` remove the FutureWarning, update the
  return type by removing ``np.asmatrix``, and update the docstring to
  reflect that the function returns a ``numpy.ndarray`` instance.
* In ``generators/small.py`` remove ``make_small_graph`` and
  ``make_small_undirected_graph``.
* In ``classes/function.py`` remove ``info``.
* In ``algorithms/community/modularity_max.py``, remove the deprecated
  ``n_communities`` parameter from the ``greedy_modularity_communities``
  function.
* In ``algorithms/distance_measures.py`` remove ``extrema_bounding``.
* In ``utils/misc.py`` remove ``dict_to_numpy_array1`` and ``dict_to_numpy_array2``.
* In ``utils/misc.py`` remove ``to_tuple``.
* In ``algorithms/matching.py``, remove parameter ``maxcardinality`` from ``min_weight_matching``.


Version 3.2
~~~~~~~~~~~
* In ``generators/directed.py`` remove the ``create_using`` keyword argument
  for the ``scale_free_graph`` function.
* Remove pydot functionality ``drawing/nx_pydot.py``, if pydot is still not being maintained. See #5723
* In ``readwrite/json_graph/node_link.py`` remove the ``attrs` keyword code 
  and docstring in ``node_link_data`` and ``node_link_graph``. Also the associated tests.
