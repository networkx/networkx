Next Release
============

Release date: TBD

Supports Python 3.7, 3.8, and 3.9.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our `gallery of examples
<https://networkx.org/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:

- Dropped support for Python 3.6.
- NumPy, SciPy, Matplotlib, and pandas are now default requirements.

Improvements
------------

- [`#4319 <https://github.com/networkx/networkx/pull/4319>`_]
  pagerank uses scipy by default now.
- [`#4317 <https://github.com/networkx/networkx/pull/4317>`_]
  New ``source`` argument to ``has_eulerian_path`` to look for path starting at
  source.
- [`#4640 <https://github.com/networkx/networkx/pull/4640>`_]
  ``prefix_tree`` now uses a non-recursive algorithm. The original recursive
  algorithm is still available via ``prefix_tree_recursive``.
- [`#4659 <https://github.com/networkx/networkx/pull/4659>`_]
  New ``initial_graph`` argument to ``barabasi_albert_graph`` and
  ``dual_barabasi_albert_graph`` to supply an initial graph to the model.

API Changes
-----------

- [`#4190 <https://github.com/networkx/networkx/pull/4190>`_]
  Removed ``tracemin_chol``.  Use ``tracemin_lu`` instead.
- [`#4216 <https://github.com/networkx/networkx/pull/4216>`_]
  In `to_*_array/matrix`, nodes in nodelist but not in G now raise an exception.
  Use G.add_nodes_from(nodelist) to add them to G before converting.
- [`#4360  <https://github.com/networkx/networkx/pull/4360>`_]
  Internally `.nx_pylab.draw_networkx_edges` now always generates a
  list of `matplotlib.patches.FancyArrowPatch` rather than using
  a `matplotlib.collections.LineCollection` for un-directed graphs.  This
  unifies interface for all types of graphs.  In
  addition to the API change this may cause a performance regression for
  large graphs.
- [`#4384 <https://github.com/networkx/networkx/pull/4384>`_]
  Added edge_key parameter for MultiGraphs in to_pandas_edgelist
- [`#4466 <https://github.com/networkx/networkx/pull/4466>`_]
  `relabel_nodes` used to raise a KeyError for a key in `mapping` that is not
  a node in the graph, but it only did this when `copy` was `False`. Now
  any keys in `mapping` which are not in the graph are ignored.
- [`#4573 <https://github.com/networkx/networkx/pull/4573>`_]
  `label_propagation_communities` returns a `dict_values` object of community
  sets of nodes instead of a generator of community sets. It is still iterable,
  so likely will still work in most user code and a simple fix otherwise:
  e.g., add `iter( ... )` surrounding the function call.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  `prefix_tree` used to return `tree, root` but root is now always 0
  instead of a UUID generate string. So the function returns `tree`.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  The variable `NIL` ="NIL" has been removed from `networkx.generators.trees`
- [`#3620 <https://github.com/networkx/networkx/pull/3620>`_]
  The function `naive_greedy_modularity_communities` now returns a
  list of communities (like `greedy_modularity_communities`) instead
  of a generator of communities.

Deprecations
------------

- [`#4238 <https://github.com/networkx/networkx/pull/4238>`_]
  Deprecate ``to_numpy_matrix`` and ``from_numpy_matrix``.
- [`#4279 <https://github.com/networkx/networkx/pull/4279>`_]
  Deprecate ``networkx.utils.misc.is_iterator``.
  Use ``isinstance(obj, collections.abc.Iterator)`` instead.
- [`#4280 <https://github.com/networkx/networkx/pull/4280>`_]
  Deprecate ``networkx.utils.misc.is_list_of_ints`` as it is no longer used.
  See ``networkx.utils.misc.make_list_of_ints`` for related functionality.
- [`#4281 <https://github.com/networkx/networkx/pull/4281>`_]
  Deprecate ``read_yaml`` and ``write_yaml``.
- [`#4282 <https://github.com/networkx/networkx/pull/4282>`_]
  Deprecate ``read_gpickle`` and ``write_gpickle``.
- [`#4298 <https://github.com/networkx/networkx/pull/4298>`_]
  Deprecate ``read_shp``, ``edges_from_line``, and ``write_shp``.
- [`#4319 <https://github.com/networkx/networkx/pull/4319>`_]
  Deprecate ``pagerank_numpy``, ``pagerank_scipy``.
- [`#4355 <https://github.com/networkx/networkx/pull/4355>`_]
  Deprecate ``copy`` method in the coreview Filtered-related classes.
- [`#4384 <https://github.com/networkx/networkx/pull/4384>`_]
  Deprecate unused ``order`` parameter in to_pandas_edgelist.
- [`#4428 <https://github.com/networkx/networkx/pull/4428>`_]
  Deprecate ``jit_data`` and ``jit_graph``.
- [`#4449 <https://github.com/networkx/networkx/pull/4449>`_]
  Deprecate ``consume``.
- [`#4448 <https://github.com/networkx/networkx/pull/4448>`_]
  Deprecate ``iterable``.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  Deprecate ``generate_unique_node``.
- [`#4599 <https://github.com/networkx/networkx/pull/4599>`_]
  Deprecate ``empty_generator``.
- [`#4617 <https://github.com/networkx/networkx/pull/4617>`_]
  Deprecate ``hub_matrix`` and ``authority_matrix``
- [`#4629 <https://github.com/networkx/networkx/pull/4629>`_]
  Deprecate the ``Ordered`` graph classes.


Contributors
------------

<output of contribs.py>


Merged PRs
----------

<output of contribs.py>
