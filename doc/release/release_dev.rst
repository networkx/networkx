Next Release
============

Release date: TBD

Supports Python 3.7, 3.8, and 3.9.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:

- Dropped support for Python 3.6.
- NumPy, SciPy, Matplotlib, and pandas are now default requirements.
- Improved example gallery
- Removed code for supporting Jython/IronPython
- The ``__str__`` method for graph objects is more informative and concise.
- Improved import time
- Improved test coverage
- New documentation theme
- Add functionality for drawing self-loop edges
- Add approximation algorithms for Traveling Salesman Problem

New functions:

- Panther algorithm
- maximum cut heuristics
- equivalence_classes
- dedensification
- random_ordered_tree
- forest_str
- snap_aggregation
- networkx.approximation.diameter
- partition_quality
- prominent_group
- prefix_tree_recursive
- topological_generations

NXEPs
-----

**N**\etwork\ **X** **E**\nhancement **P**\roposals capture changes
that are larger in scope than typical pull requests, such as changes to
fundamental data structures.
The following proposals have come under consideration since the previous
release:

- :ref:`NXEP2`
- :ref:`NXEP3`

Improvements
------------

- [`#3886 <https://github.com/networkx/networkx/pull/3886>`_]
  Adds the Panther algorithm for top-k similarity search.
- [`#4138 <https://github.com/networkx/networkx/pull/4138>`_]
  Adds heuristics for approximating solution to the maximum cut problem.
- [`#4183 <https://github.com/networkx/networkx/pull/4183>`_]
  Adds ``equivalence_classes`` to public API.
- [`#4193 <https://github.com/networkx/networkx/pull/4193>`_]
  ``nx.info`` is more concise.
- [`#4198 <https://github.com/networkx/networkx/pull/4198>`_]
  Improve performance of ``transitivity``.
- [`#4206 <https://github.com/networkx/networkx/pull/4206>`_]
  UnionFind.union selects the heaviest root as the new root
- [`#4240 <https://github.com/networkx/networkx/pull/4240>`_]
  Adds ``dedensification`` function in a new ``summarization`` module.
- [`#4294 <https://github.com/networkx/networkx/pull/4294>`_]
  Adds ``forest_str`` for string representation of trees.
- [`#4319 <https://github.com/networkx/networkx/pull/4319>`_]
  pagerank uses scipy by default now.
- [`#4841 <https://github.com/networkx/networkx/pull/4841>`_]
  simrank_similarity uses numpy by default now.
- [`#4317 <https://github.com/networkx/networkx/pull/4317>`_]
  New ``source`` argument to ``has_eulerian_path`` to look for path starting at
  source.
- [`#4356 <https://github.com/networkx/networkx/pull/4356>`_]
  Use ``bidirectional_djikstra`` in ``shortest_path`` for weighted graphs
  to improve performance.
- [`#4361 <https://github.com/networkx/networkx/pull/4361>`_]
  Adds ``nodelist`` argument to ``triadic_census``
- [`#4435 <https://github.com/networkx/networkx/pull/4435>`_]
  Improve ``group_betweenness_centrality``.
- [`#4446 <https://github.com/networkx/networkx/pull/4446>`_]
  Add ``sources`` parameter to allow computing ``harmonic_centrality`` from a
  subset of nodes.
- [`#4463 <https://github.com/networkx/networkx/pull/4463>`_]
  Adds the ``snap`` summarization algorithm.
- [`#4476 <https://github.com/networkx/networkx/pull/4476>`_]
  Adds the ``diameter`` function for approximating the lower bound on the
  diameter of a graph.
- [`#4519 <https://github.com/networkx/networkx/pull/4519>`_]
  Handle negative weights in clustering algorithms.
- [`#4528 <https://github.com/networkx/networkx/pull/4528>`_]
  Improved performance of ``edge_boundary``.
- [`#4560 <https://github.com/networkx/networkx/pull/4560>`_]
  Adds ``prominent_group`` function to find prominent group of size k in
  G according to group_betweenness_centrality.
- [`#4588 <https://github.com/networkx/networkx/pull/4588>`_]
  Graph intersection now works when input graphs don't have the same node sets.
- [`#4607 <https://github.com/networkx/networkx/pull/4607>`_]
  Adds approximation algorithms for solving the traveling salesman problem,
  including ``christofides``, ``greedy_tsp``, ``simulated_annealing_tsp``,
  and ``threshold_accepting_tsp``.
- [`#4640 <https://github.com/networkx/networkx/pull/4640>`_]
  ``prefix_tree`` now uses a non-recursive algorithm. The original recursive
  algorithm is still available via ``prefix_tree_recursive``.
- [`#4659 <https://github.com/networkx/networkx/pull/4659>`_]
  New ``initial_graph`` argument to ``barabasi_albert_graph`` and
  ``dual_barabasi_albert_graph`` to supply an initial graph to the model.
- [`#4690 <https://github.com/networkx/networkx/pull/4690>`_]
  ``modularity_max`` now supports edge weights.
- [`#4727 <https://github.com/networkx/networkx/pull/4727>`_]
  Improved performance of ``scale_free_graph``.
- [`#4757 <https://github.com/networkx/networkx/pull/4757>`_]
  Adds ``topological_generations`` function for DAG stratification.
- [`#4768 <https://github.com/networkx/networkx/pull/4768>`_]
  Improved reproducibility of geometric graph generators.
- [`#4769 <https://github.com/networkx/networkx/pull/4769>`_]
  Adds ``margins`` keyword to ``draw_networkx_nodes`` to control node clipping
  in images with large node sizes.
- [`#4812 <https://github.com/networkx/networkx/pull/4812>`_]
  Use ``scipy`` implementation for ``hits`` algorithm to improve performance.
- [`#4847 <https://github.com/networkx/networkx/pull/4847>`_]
  Improve performance of ``scipy`` implementation of ``hits`` algorithm.

API Changes
-----------

- [`#4183 <https://github.com/networkx/networkx/pull/4183>`_]
  ``partition`` argument of `quotient_graph` now accepts dicts
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
  Added ``edge_key`` parameter for MultiGraphs in to_pandas_edgelist
- [`#4461 <https://github.com/networkx/networkx/pull/4461>`_]
  Added ``create_using`` parameter to ``binomial_tree``
- [`#4466 <https://github.com/networkx/networkx/pull/4466>`_]
  `relabel_nodes` used to raise a KeyError for a key in `mapping` that is not
  a node in the graph, but it only did this when `copy` was `False`. Now
  any keys in `mapping` which are not in the graph are ignored.
- [`#4502 <https://github.com/networkx/networkx/pull/4502>`_]
  Moves ``maximum_independent_set`` to the ``clique`` module in ``approximation``.
- [`#4536 <https://github.com/networkx/networkx/pull/4536>`_]
  Deprecate ``performance`` and ``coverage`` in favor of ``partition_quality``,
  which computes both metrics simultaneously and is more efficient.
- [`#4573 <https://github.com/networkx/networkx/pull/4573>`_]
  `label_propagation_communities` returns a `dict_values` object of community
  sets of nodes instead of a generator of community sets. It is still iterable,
  so likely will still work in most user code and a simple fix otherwise:
  e.g., add ``iter( ... )`` surrounding the function call.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  `prefix_tree` used to return `tree, root` but root is now always 0
  instead of a UUID generate string. So the function returns `tree`.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  The variable `NIL` ="NIL" has been removed from `networkx.generators.trees`
- [`#3620 <https://github.com/networkx/networkx/pull/3620>`_]
  The function `naive_greedy_modularity_communities` now returns a
  list of communities (like `greedy_modularity_communities`) instead
  of a generator of communities.
- [`#4786 <https://github.com/networkx/networkx/pull/4786>`_]
  Deprecate the ``attrs`` keyword argument in favor of explicit keyword
  arguments in the ``json_graph`` module.
- [`#4843 <https://github.com/networkx/networkx/pull/4843>`_]
  The unused ``normalized`` parameter has been removed
  from ``communicability_betweeness_centrality``
- [`#4850 <https://github.com/networkx/networkx/pull/4850>`_]
  Added ``dtype`` parameter to adjacency_matrix
- [`#4867 <https://github.com/networkx/networkx/pull/4867>`_]
  The function ``spring_layout`` now ignores 'fixed' nodes not in the graph

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
- [`#4536 <https://github.com/networkx/networkx/pull/4536>`_]
  Deprecate ``performance`` and ``coverage`` in favor of ``parition_quality``.
- [`#4545 <https://github.com/networkx/networkx/pull/4545>`_]
  Deprecate ``generate_unique_node``.
- [`#4599 <https://github.com/networkx/networkx/pull/4599>`_]
  Deprecate ``empty_generator``.
- [`#4600 <https://github.com/networkx/networkx/pull/4600>`_]
  Deprecate ``default_opener``.
- [`#4617 <https://github.com/networkx/networkx/pull/4617>`_]
  Deprecate ``hub_matrix`` and ``authority_matrix``
- [`#4629 <https://github.com/networkx/networkx/pull/4629>`_]
  Deprecate the ``Ordered`` graph classes.
- [`#4802 <https://github.com/networkx/networkx/pull/4802>`_]
  The ``nx_yaml`` function has been removed along with the dependency on
  ``pyyaml``. Removal implemented via module ``__getattr__`` to patch security
  warnings related to ``pyyaml.Loader``.
- [`#4826 <https://github.com/networkx/networkx/pull/4826>`_]
  Deprecate ``preserve_random_state``.
- [`#4827 <https://github.com/networkx/networkx/pull/4827>`_]
  Deprecate ``almost_equal``.
- [`#4833 <https://github.com/networkx/networkx/pull/4833>`_]
  Deprecate ``run``.
- [`#4829 <https://github.com/networkx/networkx/pull/4829>`_]
  Deprecate ``assert_nodes_equal``, ``assert_edges_equal``, and ``assert_graphs_equal``.
- [`#4850 <https://github.com/networkx/networkx/pull/4850>`_]
  Deprecate ``adj_matrix``.
- [`#4841 <https://github.com/networkx/networkx/pull/4841>`_]
  Deprecate ``simrank_similarity_numpy``.

Contributors
------------

<output of contribs.py>


Merged PRs
----------

<output of contribs.py>
