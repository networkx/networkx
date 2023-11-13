.. _networkx_2.7:

NetworkX 2.7
============

Release date: 28 February 2022

Supports Python 3.8, 3.9, and 3.10

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 7 months of work with over 166 pull requests by
33 contributors. Highlights include:

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
  problem: `~networkx.algorithms.approximation.traveling_salesman.asadpour_atsp`.
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
  This adds support for generic attributes, such as adjacency matrices with
  complex weights. This also adds support for generic reduction functions in
  handling multigraph weights, such as ``mean`` or ``median``. Finally, this
  also includes support for structured dtypes, which enables the creation of
  multi-attribute adjacency matrices and replaces the less generic
  ``to_numpy_recarray``.
- Added support for computing betweenness centrality on multigraphs
- Added support for directed graphs and multigraphs to ``greedy_modularity_communities``.

GSoC PRs
--------

We added the work from four Google Summer of Code projects:

- `Louvain community detection algorithm`_
    - Program: Google Summer of Code 2021
    - Contributor: `@z3y50n <https://github.com/z3y50n/>`__
    - Link to Proposal:  `GSoC 2021: Community Detection Algorithms <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2021-Community-Detection-Algorithms.pdf>`__

- `Asadpour algorithm for directed travelling salesman problem`_
    - Program: Google Summer of Code 2021
    - Contributor: `@mjschwenne <https://github.com/mjschwenne/>`__
    - Link to Proposal:  `GSoC 2021: Asadpour algorithm <https://github.com/networkx/archive/blob/main/proposals-gsoc/GSoC-2021-Asadpour-Asymmetric-Traveling%20Salesman-Problem.pdf>`__

- Pedagogical notebook: `Directed acyclic graphs and topological sort`_
    - Program: Google Summer of Code 2021
    - Contributor:  `@vdshk <https://github.com/vdshk>`__

- Pedagogical notebooks: `Graph assortativity`_ & `Network flow analysis and Dinitz algorithm`_
    - Program: Google Summer of Code 2021
    - Contributor: `@harshal-dupare <https://github.com/harshal-dupare/>`__

.. _`Louvain community detection algorithm`: https://github.com/networkx/networkx/pull/4929
.. _`Asadpour algorithm for directed travelling salesman problem`: https://github.com/networkx/networkx/pull/4740
.. _`Directed acyclic graphs and topological sort`: https://github.com/networkx/nx-guides/pull/44
.. _`Graph assortativity`: https://github.com/networkx/nx-guides/pull/42
.. _`Network flow analysis and Dinitz algorithm`: https://github.com/networkx/nx-guides/pull/46

Improvements
------------

- [`#4740 <https://github.com/networkx/networkx/pull/4740>`_]
  Add the Asadpour algorithm for solving the asymmetric traveling salesman
  problem.
- [`#4897 <https://github.com/networkx/networkx/pull/4897>`_]
  Improve the validation and performance of ``nx.is_matching``,
  ``nx.is_maximal_matching`` and ``nx.is_perfect_matching``.
- [`#4924 <https://github.com/networkx/networkx/pull/4924>`_]
  Fix handling of disconnected graphs when computing
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
  Improve readability of ``node_classification`` functions.
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
  Add support for `None` edge weights to bidirectional Dijkstra algorithm.
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
- [`#5341 <https://github.com/networkx/networkx/pull/5341>`_]
  Deprecate redundant ``info``.

Merged PRs
----------

A total of 166 changes have been committed.

- Support `comments=None` in read/parse edgelist (#5051)
- Add see also refs to de/stringizers in gml docstrings. (#5053)
- Add weisfeiler lehman subgraph hashing (#4946)
- Deprecate `random_state` decorator (#5055)
- Bug fix for issue #5023 :  corner-case bug in single_source_dijkstra (#5033)
- More informative GraphML exceptions (#5058)
- Minor updates to tutorial.rst and add docstring for data method of nodes/edges (#5039)
- Document `geometric_edges` and add it to main namespace (#5045)
- Fix small typo in `trophic_levels` documentation (#5087)
- Refactor `transitive_closure` (#5052)
- Fix fast_gnp_random_graph for directed graphs (issue #3389) (#5077)
- Get number of edges by calling the proper method (#5095)
- Update mentored projects section in docs (#5056)
- Parametrize shortest path node-checking tests. (#5078)
- Create FUNDING.yml
- Deprecate union name param (#5114)
- Update FUNDING.yml
- vertex_cover: Added support for self-loop nodes (#5104)
- Update core dev team (#5119)
- Faster operators in algorithms/operators/all.py (#5121)
- DOC: Add links to proposals for completed projects (#5122)
- Consistent return type in dictionary output of rescale_layout and rescale_layout_dict (#5091)
- Change exception varname e to err (#5130)
- minor tweaks in assortativity docs and code (#5129)
- Allow edge style to be a list of styles for DiGraphs (#5131)
- Add examples and minor documentation refactor for operators/binary.py (#5099)
- Improve random graphs test suite for gnp generators (issue #5092) (#5115)
- Add note about checking for path existence to all_simple_paths. (#5059)
- Fix message of raised exception in decorators. (#5136)
- Refactor linestyle test for FancyArrowPatches. (#5132)
- Drop Py37 (#5143)
- Use math.hypot (#5145)
- Add pyupgrade to pre-commit (#5146)
- Test on Python 3.10 (#4807)
- Use black 21.9b0 (#5148)
- Use sphinx 4.2 (#5150)
- Update example requirements (#5151)
- Update nx_pylab drawing edge color and width tests (#5134)
- Refactor node_classification to improve conciseness and readability (#5144)
- Add temporary pyparsing pin to fix CI. (#5156)
- Add option for arrowsize to be a list (#5154)
- List policies (#5159)
- Bugfix for issue 5123 (#5153)
- Test scipy and pandas on py3.10 (#5174)
- Deprecate `hmn` and `lgc` modules from the `node_classification` package (#5166)
- Rm passing ax.transOffset to LineCollection. (#5173)
- Add a function to find the negative cycle using bellman_ford (#5089)
- Add a Q&A to the contributor FAQ about algorithm acceptance policy. (#5177)
- DOC: Fix typo in docs for weighted shortest paths (#5181)
- Revert "Add temporary pyparsing pin to fix CI. (#5156)" (#5180)
- Only compute shortest path lengths when used (#5183)
- Add Mypy type checking infrastructure (#5127)
- xfail pydot tests. (#5187)
- Remove unused internal solver from algebraicconnectivity (#5190)
- Remove check/comment for scipy 1.1 behavior. (#5191)
- Test on Python 3.10 (#5185)
- Add regression test for ancestors/descendants w/ undir. G. (#5188)
- Rm internal function, use advanced indexing instead. (#5197)
- Fix missing import + tests in laplacian fns. (#5194)
- Investigate pre-release test failures (#5208)
- Rm assertion method in favor of assert statements. (#5214)
- Remove unused variable in mycielski.py (#5210)
- used queue instead of ordinary list (#5217)
- Add FutureWarning about matrix->array output to `google_matrix` (#5219)
- A few `np.matrix` cleanups (#5218)
- Rm internal laplacian in favor of laplacian_matrix. (#5196)
- [MRG] Create plot_subgraphs.py example (#5165)
- Add traveling salesman problem to example gallery (#4874)
- Fixed inconsistent documentation for nbunch parameter in DiGraph.edges() (#5037)
- Compatibility updates from testing with numpy/scipy/pytest rc's (#5226)
- Replace internal `close` fn with `math.isclose`. (#5224)
- Fix Python 3.10 deprecation warning w/ int div. (#5231)
- Touchups and suggestions for subgraph gallery example (#5225)
- Use new package name (#5234)
- Allowing None edges in weight function of bidirectional Dijkstra (#5232)
- Add an FAQ about assigning issues. (#5182)
- Update dev deps (#5243)
- Update minor doc issues with tex notation (#5244)
- Minor changes to speed up asynchronous label propagation for community detection. (#5247)
- Docstrings for the small.py module (#5240)
- Use scipy.sparse array datastructure (#5139)
- Update sphinx (#5272)
- Update year (#5273)
- Update extra dependencies (#5263)
- Update gexf website link in documentation (#5275)
- Update numpydoc (#5274)
- Initial setup of lazy_import functions. (#4909)
- Deprecate scipy sparse matrix conversion functions (#5262)
- Fix lowest_common_ancestors (issue #4942) (#5086)
- Make small graph generator node test more specific. (#5282)
- Use from_dict_of_lists instead of make_small_graph in generators.small (#5267)
- Refactor `to_numpy_array` with advanced indexing (#5250)
- Fix: Update louvain_partitions for threshold (update mod to new_mod in each level) (#5284)
- Add exception for unconnected graph (#5287)
- Fixing Tarjan's strongly connected components algorithm implementation to have `O(|E|+|V|)` time complexity instead of `O(|V|^3)`. (#5288)
- Add weights to karate club graph (#5285)
- Fix functions appearing in variables `__all__` but not in docs for NX2.7 (#5289)
- Update to stable version of black (#5296)
- Add FutureWarning to `attr_matrix` to notify users of return type change (#5300)
- DOC: change status to accepted for NXEP2, add resolution (#5297)
- Update test requirements (#5304)
- Update scipy (#5276)
- DOC: Update documentation to include callables for weight argument (#5307)
- Update pygraphviz (#5314)
- Document default dtype in to_numpy_recarray docstring. (#5315)
- Rm unused AbstractSet. (#5317)
- Deprecate `make_small_graph` and `make_small_undirected_graph` (#5283)
- Update `draw_<layout>` docstrings with usage examples (#5264)
- More numpy.matrix cleanups for NX2.7 (#5319)
- MAINT: Cleanup assortativity module, remove unused variables (#5301)
- Add informative exception for drawing multiedge labels. (#5316)
- Potential resolution to full paths to functions in docs (#5049)
- MAINT: Cleanup link analysis module, remove unused variables (#5306)
- Use pytest-mpl (#4579)
- Keep omega within [-1, 1] bounds (#5216)
- Add support for finding maximal cliques containing a set of nodes (#5172)
- MAINT: Remove unnecessary helper functions, use inbuilt methods for line graph generator (#5327)
- sampling from dict_keys objects is deprecated. (#5337)
- Add support for `numpy.random.Generator` (#5336)
- Update matching functions for error validation and speed (#4897)
- Update release requirements (#5338)
- Add structured dtypes to `to_numpy_array` (#5324)
- Deprecate `to_numpy_recarray` (#5330)
- First pass at 2.7 release notes. (#5342)
- Add pickle and yaml migration info (#5345)
- Deprecate info (#5341)
- Fix pandas warning (#5346)
- Test on 3.11-dev (#5339)
- Designate 2.7rc1 release
- Bump release version
- Update release process (#5348)
- Update mentored project info with the expected time commitment (#5349)
- Use np.random.default_rng in example + other updates. (#5356)
- Remove stuff conda doesn't support (#5361)
- Fix spiral_layout when equidistant=True (#5354)
- Fix docs (#5364)

Contributors
------------

- Will Badart
- Ross Barnowski
- Mathieu Bastian
- Martin Becker
- Anutosh Bhat
- Alejandro Candioti
- Divyansh
- Andrew Eckart
- Yossi Eliaz
- Casper van Elteren
- Simone Gasperini
- Daniel Haden
- Leo Klarner
- Andrew Knyazev
- Fabrizio Kuruc
- Paarth Madan
- Jarrod Millman
- Achille Nazaret
- NikHoh
- Sultan Orazbayev
- Dimitrios Papageorgiou
- Aishwarya Ramasethu
- Ryuki
- Katalin Schmidt
- Dan Schult
- Mridul Seth
- Cirus Thenter
- James Trimble
- Vadim
- Hnatiuk Vladyslav
- Aaron Z
- eskountis
- kpberry
