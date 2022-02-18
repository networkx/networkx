Next Release
============

Release date: TBD

Supports Python 3.8, 3.9, and 3.10

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of X of work with over X pull requests by
X contributors. Highlights include:

.. warning::
   Hash values observed in outputs of 
   `~networkx.algorithms.graph_hashing.weisfeiler_lehman_graph_hash`
   have changed in version 2.7 due to bug fixes. See gh-4946_ for details.
   This means that comparing hashes of the same graph computed with different
   versions of NetworkX (i.e. before and after version 2.7)
   could wrongly fail an isomorphism test (isomorphic graphs always have matching
   Weisfeiler-Lehman hashes). Users are advised to recalculate any stored graph
   hashes they may have on upgrading.

.. _gh-4946: https://github.com/networkx/networkx/pull/4946#issuecomment-914623654

- Dropped support for Python 3.7.
- Added the Asadpour algorithm for solving the asymmetric traveling salesman
  problem: `~networkx.algorithms.approximation.asadpour_atsp`.
- Added the Louvain community detection algorithm:
  `~networkx.algorithms.community.louvain.louvain_communities` and
  `~networkx.algorithms.community.louvain.louvain_partitions`
- Removed all internal usage of the `numpy.matrix` class, and added a
  `FutureWarning` to all functions that return a `numpy.matrix` instance.
  The `numpy.matrix` class will be replaced with 2D `numpy.ndarray` instances
  in NetworkX 3.0.
- Added support for the `scipy.sparse` array interface. This includes
  `~networkx.convert_matrix.to_scipy_sparse_array` and
  `~networkx.convert_matrix.from_scipy_sparse_array`. In NetworkX 3.0,
  sparse arrays will replace sparse matrices as the primary interface to
  `scipy.sparse`. New code should use ``to_scipy_sparse_array`` and
  ``from_scipy_sparse_array`` instead of their matrix counterparts.
  In addition, many functions that currently return sparse matrices now raise
  a `FutureWarning` to indicate that they will return sparse arrays instead in
  NetworkX 3.0.
- Added generic dtype support to `~networkx.convert_matrix.to_numpy_array`.
  This adds support for generic attributes, such as adjaceny matrices with
  complex weights. This also add support for generic reduction functions in
  handling multigraph weights, such as ``mean`` or ``median``. Finally, this
  also includes support for structured dtypes, which enables the creation of
  multi-attribute adjacency matrices and replaces the less generic
  ``to_numpy_recarray``.

**Maybes**
- Added support for computing betweenness centrality on multigraphs
  Add support for directed graphs and multigraphs to ``greedy_modularity_communities``.
- Add note about MyPy? I vote no so as not to mislead users that we have
  type annotations now.

**TODO**
GSoC PRs
--------
4740, 4929, 5017, 5019, 5052

Improvements
------------

- [`#4740 <https://github.com/networkx/networkx/pull/4740>`_]
  Add the Asadpour algorithm for solving the asymmetric traveling salesman
  problem.
- [`#4897 <https://github.com/networkx/networkx/pull/4897>`_]
  Improve the validation and performance of ``nx.is_matching``,
  ``nx.is_maximal_matching`` and ``nx.is_perfect_matcing``.
- [`#4924 <https://github.com/networkx/networkx/pull/4924>`_]
  Fix handling of disconnected graphs whne computing
  ``nx.common_neighbor_centrality``.
- [`#4929 <https://github.com/networkx/networkx/pull/4929>`_]
  Add Louvain community detection.
- [`#4946 <https://github.com/networkx/networkx/pull/4946>`_]
  Add Weisfeiler-Lehman hashing subgraph hashing.
- [`#4950 <https://github.com/networkx/networkx/pull/4950>`_]
  Add an ``n_communities`` parameter to ``greedy_modularity_communities`` to
  terminate the search when the desired number of communities is found.
- [`#4965 <https://github.com/networkx/networkx/pull/4965>`_] and
  [`#4996 <https://github.com/networkx/networkx/pull/4996>`_]
  Fix handling of relabeled nodes in ``greedy_modularity_communities``.
- [`#4976 <https://github.com/networkx/networkx/pull/4976>`_]
  Add betweenness centrality for multigraphs.
- [`#4999 <https://github.com/networkx/networkx/pull/4999>`_]
  Fix ``degree_assortativity_coefficient`` for directed graphs.
- [`#5007 <https://github.com/networkx/networkx/pull/5007>`_]
  Add support for directed graphs and multigraphs to ``greedy_modularity_communities``.
- [`#5017 <https://github.com/networkx/networkx/pull/5017>`_]
  Improve implementation and documentation of ``descendants`` and ``ancestors``
- [`#5019 <https://github.com/networkx/networkx/pull/5019>`_]
  Improve documentation and testing for directed acyclic graph module.
- [`#5029 <https://github.com/networkx/networkx/pull/5029>`_]
  Improve documentation and testing of ``descendants_at_distance``.
- [`#5032 <https://github.com/networkx/networkx/pull/5032>`_]
  Improve performance of ``complement_edges``.
- [`#5045 <https://github.com/networkx/networkx/pull/5045>`_]
  Add ``geometric_edges`` to the ``nx`` namespace.
- [`#5051 <https://github.com/networkx/networkx/pull/5051>`_]
  Add support for comment characters for reading data with ``read_edgelist``.
- [`#5052 <https://github.com/networkx/networkx/pull/5052>`_]
  Improve performance and add support for undirected graphs and multigraphs to
  ``transitive_closure``.
- [`#5058 <https://github.com/networkx/networkx/pull/5058>`_]
  Improve exception handling for writing data in GraphML format.
- [`#5065 <https://github.com/networkx/networkx/pull/5065>`_]
  Improve support for floating point weights and resolution values in
  ``greedy_modularity_communities``.
- [`#5077 <https://github.com/networkx/networkx/pull/5077>`_]
  Fix edge probability in ``fast_gnp_random_graph`` for directed graphs.
- [`#5086 <https://github.com/networkx/networkx/pull/5086>`_]
  Fix defect in ``lowest_common_ancestors``.
- [`#5089 <https://github.com/networkx/networkx/pull/5089>`_]
  Add ``find_negative_cycle`` for finding negative cycles in weighted graphs.
- [`#5099 <https://github.com/networkx/networkx/pull/5099>`_]
  Improve documentation and testing of binary operators.
- [`#5104 <https://github.com/networkx/networkx/pull/5104>`_]
  Add support for self-loop edges and improve performance of ``vertex_cover``.
- [`#5121 <https://github.com/networkx/networkx/pull/5121>`_]
  Improve performance of ``*_all`` binary operators.
- [`#5131 <https://github.com/networkx/networkx/pull/5131>`_]
  Allow ``edge_style`` to be a list of styles when drawing edges for DiGraphs.
- [`#5139 <https://github.com/networkx/networkx/pull/5139>`_]
  Add support for the `scipy.sparse` array interface.
- [`#5144 <https://github.com/networkx/networkx/pull/5144>`_]
  Improve readibility of ``node_classification`` functions.
- [`#5145 <https://github.com/networkx/networkx/pull/5145>`_]
  Adopt `math.hypot` which was added in Python 3.8.
- [`#5153 <https://github.com/networkx/networkx/pull/5153>`_]
  Fix ``multipartite_layout`` for graphs with non-numeric nodes.
- [`#5154 <https://github.com/networkx/networkx/pull/5154>`_]
  Allow ``arrowsize`` to be a list of arrow sizes for drawing edges.
- [`#5172 <https://github.com/networkx/networkx/pull/5172>`_]
  Add a ``nodes`` keyword argument to ``find_cliques`` to add support for
  finding maximal cliques containing only a set of nodes.
- [`#5197 <https://github.com/networkx/networkx/pull/5197>`_]
  Improve ``resistance_distance`` with advanced indexing.
- [`#5216 <https://github.com/networkx/networkx/pull/5216>`_]
  Make ``omega()`` closer to the published algorithm. The value changes slightly.
  The ``niter`` parameter default changes from 1->5 in ``lattice_reference()``
  and from 100->5 in ``omega``.
- [`#5217 <https://github.com/networkx/networkx/pull/5217>`_]
  Improve performance and readability of ``betweenness_centrality``.
- [`#5232 <https://github.com/networkx/networkx/pull/5232>`_]
  Add support for `None` edge weights to bidirectional Djikstra algorithm.
- [`#5247 <https://github.com/networkx/networkx/pull/5247>`_]
  Improve performance of asynchronous label propagation algorithm for
  community detection, ``asyn_lpa_communities``.
- [`#5250 <https://github.com/networkx/networkx/pull/5250>`_]
  Add generic dtype support to ``to_numpy_array``.
- [`#5285 <https://github.com/networkx/networkx/pull/5285>`_]
  Improve ``karate_club_graph`` by updating to the weighted version from the original
  publication.
- [`#5287 <https://github.com/networkx/networkx/pull/5287>`_]
  Improve input validation for ``json_graph``.
- [`#5288 <https://github.com/networkx/networkx/pull/5288>`_]
  Improve performance of ``strongly_connected_components``.
- [`#5324 <https://github.com/networkx/networkx/pull/5324>`_]
  Add support for structured dtypes to ``to_numpy_array``.
- [`#5336 <https://github.com/networkx/networkx/pull/5336>`_]
  Add support for the `numpy.random.Generator` interface for random number
  generation.

API Changes
-----------

- The values in the dictionary returned by
  `~networkx.drawing.layout.rescale_layout_dict` are now `numpy.ndarray` objects
  instead of tuples. This makes the return type of ``rescale_layout_dict``
  consistent with that of all of the other layout functions.
- A ``FutureWarning`` has been added to ``google_matrix`` to indicate that the
  return type will change from a ``numpy.matrix`` object to a ``numpy.ndarray``
  in NetworkX 3.0.
- A ``FutureWarning`` has been added to ``attr_matrix`` to indicate that the
  return type will change from a ``numpy.matrix`` object to a ``numpy.ndarray``
  object in NetworkX 3.0.
- The ``is_*_matching`` functions now raise exceptions for nodes not in G in
  any edge.

Deprecations
------------

- [`#5055 <https://github.com/networkx/networkx/pull/5055>`_]
  Deprecate the ``random_state`` alias in favor of ``np_random_state``
- [`#5114 <https://github.com/networkx/networkx/pull/5114>`_]
  Deprecate the ``name`` kwarg from ``union`` as it isn't used.
- [`#5143 <https://github.com/networkx/networkx/pull/5143>`_]
  Deprecate ``euclidean`` in favor of ``math.dist``.
- [`#5166 <https://github.com/networkx/networkx/pull/5166>`_]
  Deprecate the ``hmn`` and ``lgc`` modules in ``node_classification``.
- [`#5262 <https://github.com/networkx/networkx/pull/5262>`_]
  Deprecate ``to_scipy_sparse_matrix`` and ``from_scipy_sparse_matrix`` in
  favor of ``to_scipy_sparse_array`` and ``from_scipy_sparse_array``, respectively.
- [`#5283 <https://github.com/networkx/networkx/pull/5283>`_]
  Deprecate ``make_small_graph`` and ``make_small_undirected_graph`` from the
  ``networkx.generators.small`` module.
- [`#5330 <https://github.com/networkx/networkx/pull/5330>`_]
  Deprecate ``to_numpy_recarray`` in favor of ``to_numpy_array`` with a
  structured dtype.


Merged PRs
----------

<output of contribs.py>


Contributors
------------

<output of contribs.py>
