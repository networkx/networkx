.. _networkx_2.6:

NetworkX 2.6
============

Release date: 08 July 2021

Supports Python 3.7, 3.8, and 3.9.

This release has a larger than normal number of changes in preparation for the upcoming 3.0 release.
The current plan is to release 2.7 near the end of summer and 3.0 in late 2021.
See :doc:`migration_guide_from_2.x_to_3.0` for more details.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 11 months of work with over 363 pull requests by
91 contributors. Highlights include:

- Dropped support for Python 3.6
- Dropped "decorator" library dependency
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
  Use ``bidirectional_dijkstra`` in ``shortest_path`` for weighted graphs
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
- [`#4739 <https://github.com/networkx/networkx/pull/4739>`_]
  Added `argmap` function to replace the decorator library dependence
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
  from ``communicability_betweenness_centrality``
- [`#4850 <https://github.com/networkx/networkx/pull/4850>`_]
  Added ``dtype`` parameter to adjacency_matrix
- [`#4851 <https://github.com/networkx/networkx/pull/4851>`_]
  Output of `numeric_mixing_matrix` and `degree_mixing_matrix` no longer
  includes rows with all entries zero by default. The functions now accept
  a parameter `mapping` keyed by value to row index to identify each row.
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
  Deprecate ``performance`` and ``coverage`` in favor of ``partition_quality``.
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
- [`#4923 <https://github.com/networkx/networkx/pull/4923>`_]
  Deprecate ``numeric_mixing_matrix``.
- [`#4937 <https://github.com/networkx/networkx/pull/4937>`_]
  Deprecate ``k_nearest_neighbors``.

Merged PRs
----------

- Bump release version
- Update release process
- Update website doc
- fix issue #4173: cytoscape_graph(input_data) did modify the original data (#4176)
- Some docstring fixes for draw_networkx_edge_labels() in nx_pylab.py + one typo (#4182)
- TST: add dtype to pandas test (#4185)
- Partitions for quotient graphs (#4183)
- graphml: re-add graph attribute type 'long' after 857aa81 removed it (#4189)
- Test mac osx via actions (#4201)
- DOC: Update docstrings in cytoscape module (#4180)
- rewrite add_nodes_from to relax code meant to allow ironpython pre-2.7.5 (#4200)
- Speed up transitivity, remove redundant call (#4198)
- NXEP 2 — API design of view slices (#4101)
- Cleanup old platforms (#4202)
- Fixed "topological_sort" typo (#4211)
- Make optional dependencies default on CPython
- Simplify imports
- Populate setup.py requires from requirements
- Update dependencies
- Remove _CholeskySolver
- to_numpy/scipy array functions should not allow non-nodes in nodelist (#4216)
- fix "see also" links in json_graph.tree (#4222)
- MAINT: changed is_string_like to isinstance (#4223)
- Fix UnionFind.union to select the heaviest root as the new root (#4206)
- CI: Configure circleCI to deploy docs. (#4134)
- MAINT: Update nx.info (#4193)
- Fix indexing in kernighan_lin_bisection (#4177)
- CI: Add GH fingerprint (#4229)
- Create ssh dir for circleci
- CI: update circleci doc deployment. (#4230)
- Revert "CI: Configure circleCI to deploy docs. (#4134)" (#4231)
- DOC: Add discussion to NXEP 2.
- Update format dependencies
- Use black for linting
- Format w/ black==20.8b1
- Check formatting of PRs via black (#4235)
- TST: Modify heuristic for astar path test. (#4237)
- MAINT: Deprecate numpy matrix conversion functions (#4238)
- Add roadmap (#4234)
- Add nx.info to str dunder for graph classes (#4241)
- DOC: Minor reformatting of contract_nodes docstring. (#4245)
- Fix betweenness_centrality doc paper links (#4257)
- Fix bug in has_eulerian_path for directed graphs  (#4246)
- Add PR template (#4258)
- Use seed to make plot fixed (#4260)
- Update giant component example (#4267)
- Update "house with colors" gallery example (#4263)
- Replace degree_histogram and degree_rank with a single example (#4265)
- Update Knuth miles example. (#4251)
- Update "four_grids" gallery example (#4264)
- Improve legibility of labels in plot_labels_and_colors example (#4266)
- Improve readability of chess_example in gallery (#4252)
- Fix contracted_edge for multiple edges (#4274)
- Add seeds to gallery examples for reproducibility (#4276)
- Add a 3D plotting example with matplotlib to the gallery (#4268)
- Deprecate `utils.is_iterator` (#4279)
- Deprecate utils.is_list_of_ints (#4280)
- Improve axes layout in plot_decomposition example (#4278)
- Update homepage URL (#4285)
- Build docs for deployment on Travis CI (#4286)
- Add simple graph w/ manual layout (#4291)
- Deprecate nx_yaml (#4281)
- Deprecate gpickle (#4282)
- Improve relabel coverage, tweak docstrings (#4299)
- Switch to travis-ci.com
- TST: Increase test coverage of convert_matrix (#4301)
- Add descriptive error message for Node/EdgeView slicing. NEXP2 (#4300)
- Don't import other people's version.py (#4289)
- TST: Refactor to improve coverage. (#4307)
- Improve readwrite test coverage (#4310)
- Fix typo (#4312)
- Update docstring of to_dict_of_dicts.
- Add tests for edge_data param.
- Minor touchups to docstring
- adds dedensification function (#4240)
- TST: improve multigraph test coverage to 100% (#4340)
- Add rainbow coloring example to gallery. (#4330)
- Test on Python 3.9 (#4303)
- Sphinx33 (#4342)
- fix order of yield and seen.update in all cc routines (see #4331 & #3859 & 3823) (#4333)
- Updates to slicing error message for reportviews (#4304)
- Eulerian path fix (#4317)
- Add FutureWarning in preparation for simplifying cytoscape function signatures. (#4284)
- Move a few imports inside functions to improve import speed of the library (#4296)
- Address comments from code review.
- Cleanup algebraicconnectivity (#4287)
- Switch from travis to gh actions (#4320)
- Fix (#4345)
- Fix travis doc deployment
- Fix gdal version on travis
- Update to_dict_of_dict edge_data (#4321)
- Update adjacency_iter to adjacency (#4339)
- Test and document missing nodes/edges in set_{node/edge}_attributes (#4346)
- Update tests and docs for has_eulerian_path (#4344)
- Deprecate nx_shp (#4298)
- Refactor and improve test coverage for restricted_view and selfloop_edges (#4351)
- Enable mayavi in sphinx gallery. (#4297)
- CI: Add mayavi conf to travis and GH for doc deploy (#4354)
- Fix doc build w/ GH actions
- Install vtk before mayavi
- Install vtk before mayavi
- Install vtk before mayavi
- Use bidirectional_dijkstra as default in weighted shortest_path (#4356)
- Add unit tests for utils.misc.flatten (#4359)
- Improve test coverage for coreviews.py (#4355)
- Update tutorial.rst - Fixes #4249 (#4358)
- Bugfix for issue 4336, moving try/except and adding else clause (#4365)
- Added nodelist attribute to triadic_census (#4361)
- API: always use list of FancyArrowPatch rather than LineCollection (#4360)
- MNT: make the self-loop appear in all cases (#4370)
- Add additional libraries to intersphinx mapping (#4372)
- Make nx.pagerank a wrapper around different implementations, use scipy one by default (#4319)
- MAINT: remove deprecated numpy type aliases. (#4373)
- DOC: Fix return type for random_tournament and hamiltonian_path (#4376)
- Skip memory leak test for PyPy (#4385)
- add OSMnx example (#4383)
- Update docstring for to_pandas_edgelist and add edgekey parameter (#4384)
- TST: Boost test coverage of nx_pylab module (#4375)
- Fixed issue where edge attributes were being silently overwritten during node contraction (#4273)
- CI: Fix CircleCI doc build failure (#4388)
- Improve test coverage of convert module (#4306)
- Add gene-gene network (#4269)
- Ignore expected warnings (#4391)
- Use matrix multiplication operator (#4390)
- code and doc fix for square_clustering algorithm in cluster.py (#4392)
- Remove xml import checks (#4393)
- fix typo in NXEP template (#4396)
- Add Panther algorithm per #3849 (#3886)
- Pagerank followup (#4399)
- Don't import nx from networkx (#4403)
- Modify and document behavior of nodelist param in draw_networkx_edges. (#4378)
- Add circuit plot (#4408)
- Add words graph plot (#4409)
- DOC: Remove repeated words (#4410)
- Add plot for rcm example (#4411)
- Fix small index iteration bug in kernighan_lin algorithm (#4398)
- Use str dunder (#4412)
- Use xetex for uft8 latex backend (#4326)
- Add recommended fonts to travis.yml. (#4414)
- CI: Workaround font naming bug. (#4416)
- DOC: geospatial example using lines (#4407)
- Add plotting examples for geospatial data (#4366)
- Increase coverage in graphviews.py (#4418)
- Refactor gallery (#4422)
- Safer repr format of variables (#4413)
- Updates to docs and imports for classic.py (#4424)
- Remove advanced example section (#4429)
- Add coreview objects to documentation (#4431)
- Add gallery example for drawing self-loops. (#4430)
- Add igraph example (#4404)
- Standard imports (#4401)
- Collect graphviz examples (#4427)
- NXEP 3: Allow generators to yield from edgelists (#4395)
- Update geospatial readme (#4417)
- DOC: Fix broken links in shortest_path docstrings (#4434)
- Improves description bfs_predecessors and bfs_successors. (#4438)
- Deprecate jit (#4428)
- JavaScript example: fix link (#4450)
- Deprecate utils.misc.consume (#4449)
- DOC: Switch from napoleon to numpydoc sphinx extension (#4447)
- Correct networkxsimplex docstring re: multigraph
- Correct networkxsimplex docstring re: multigraph (#4455)
- Maxcut heuristics (#4138)
- binomial_tree() with "create_using parameter (#4461)
- Reorganize tests (#4467)
- Drop Py3.6 support per NEP 29 (#4469)
- Add random_ordered_tree and forest_str (#4294)
- Deprecate iterable (#4448)
- Allow relabel_nodes mapping to have non-node keys that get ignored (#4466)
- Fixed docs + added decorator for k_components approx (#4474)
- Update docs for clustering Fixes #4348 (#4477)
- Handle self-loops for single self-loop (drawing) (#4425)
- Update GH actions links in README (#4482)
- Improve code coverage for cuts.py (#4473)
- Re-enable tests (#4488)
- Update Sphinx (#4494)
- Update pre-commit (#4495)
- Simplify example dependencies (#4506)
- Update geospatial readme (#4504)
- Update year (#4509)
- Drop Travis CI (#4510)
- Run pypy tests separately (#4512)
- Simplify version information (#4492)
- Delete old test (#4513)
- Gallery support for pygraphviz examples (#4464)
- TST: An approach to parametrizing read_edgelist tests. (#4292)
- Setup cross-repo doc deploy via actions. (#4480)
- use issue templates to redirect to discussions tab, add a bug report template (#4524)
- Fix performance issue in nx.edge_boundary (#4528)
- clean up list comp (#4499)
- Improve code coverage of swap.py (#4529)
- Clustering for signed weighted graphs (#4519)
- Fix docstrings and remove unused variables (#4501)
- Improving code coverage of chordal.py (#4471)
- Cliques on multigraph/directed graph types (#4502)
- Approximated Diameter  (#4476)
- `arrows` should be True by default for directed graphs (#4522)
- Remove unnecessary node_list from gallery example (#4505)
- fixing the width argument description of the function draw_networkx (#4479)
- Partially revert #4378 - Modify behavior of nodelist param in draw_networkx_edges. (#4531)
- Replace generate_unique_node internally where not needed (#4537)
- Extend harmonic centrality to include source nodes (#4446)
- improve group betweenness centrality (#4435)
- fixes GitHub Actions failures (#4548)
- updated cutoff def in weighted.py (#4546)
- Less strict on mayavi constraint for doc building. (#4547)
- Update docstring for ancestor and descendents (#4550)
- TST: Fix error in katz centrality test setup. (#4554)
- Correct mu parameter documentation for LFR (#4557)
- Pin pygeos==0.8 (#4563)
- Unpin pygeos (#4570)
- Test Windows via GH actions (#4567)
- Update documentation and testing of arbitrary_element (#4451)
- added test for max_iter argument
- reformatted test_kernighan_lin.py
- Simplify test pylab (#4577)
- Update README.rst
- Fix search (#4580)
- Add test Kernighan Lin Algorithm (#4575)
- Fix typos (#4581)
- Boiler plate for mentored projects documentation (#4576)
- Deprecate generate_unique_node (#4545)
- Check nodelist input to floyd_warshall (#4589)
- Improve intersection function (#4588)
- Pygraphviz choco (#4583)
- Add prominent group algorithm (#4560)
- Add partition_quality to compute coverage and performance  (coverage and perfor… (#4536)
- Use Pillow for viewing AGraph output and deprecate default_opener (#4600)
- Remove mktemp usage (#4593)
- Add an FAQ to the developer guide for new contributors (#4556)
- Improve test coverage and docs for nonrandomness (#4613)
- Collect label propagation communities in one go (#4573)
- Deprecate networkx.utils.empty_generator. (#4599)
- return earlier from `clique.graph_clique_number` (#4622)
- More for projects page: TSP and Graph Isomorphism (#4620)
- add recommended venv directory to .gitignore (#4619)
- adding weight description to centrality metrics (#4610)
- Add a good first issue badge to README  (#4627)
- add test to regular (#4624)
- Add scipy-1.6.1 to blocklist. (#4628)
- Deprecate hub_matrix and authority_matrix (#4617)
- Fix issue #3153: generalized modularity maximization  (#3260)
- Improve doc example for find_cycle. (#4639)
- Correct and update Atlas example (#4635)
- Remove attr_dict from parameters list in the docstring (#4642)
- Verify edges are valid in is_matching() (#4638)
- Remove old file reference (#4646)
- Deprecate Ordered graph classes (#4629)
- Update CI to use main (#4651)
- Make main default branch (and remove gitwash) (#4649)
- Fix link for Katz centrality definition (#4655)
- fix for negative_edge_cycle weight kwarg to bellman_ford (#4658)
- Refactor bipartite and multipartite layout (#4653)
- Volunteering for mentorship (#4671)
- Adding an iterative version of prefix tree (#4640)
- Increase code coverage tournament (#4665)
- Fix to_vertex_cover (#4667)
- Reorganize minor submodule as subpackage (#4349)
- modularity_max: account for edge weights (#4690)
- Remove instances of random.sample from sets (deprecated in Python 3.9) (#4602)
- Fixing Bug in Transitive Reduction, resulting in loss of node/edge attributes (#4684)
- direct links to the tutorial and discussions in README (#4711)
- Pin upper bound of decorator dep. (#4721)
- fix typo (#4724)
- Updating average_clustering() documentation - Issue #4734 (#4735)
- rm nx import from docstring example. (#4738)
- CI: persist pip cache between circleci runs (#4714)
- Use pydata sphinx theme (#4741)
- O(n^2) -> O(n) implementation for scale_free_graph (#4727)
- TST: be more explicit about instance comparison. (#4748)
- fix typo in docstring (ismorphism -> isomorphism) (#4756)
- CI: Fix cartopy build failure in docs workflow (#4751)
- Add missing __all__'s to utils modules + test. (#4753)
- Add 2 articles for TSP project as references (#4758)
- Improve reproducibility of geometric graphs (#4768)
- Updated decorator requirement for #4718 (#4773)
- Gallery Example: Drawing custom node icons on network using MPL (#4633)
- Get rid of invalid escape sequences. (#4789)
- imread(url) is deprecated, use pillow + urllib to load image from URL (#4790)
- Add auto-margin scaling in draw_networkx_nodes function (fix for issue 3443) (#4769)
- Update documentation dependencies (#4794)
- Fix sphinx warnings during doc build. (#4795)
- Remove mayavi and cartopy dependencies (#4800)
- make plots less dense, enable plotting for igraph (#4791)
- fix urllib import (#4793)
- Improve documentation look (#4801)
- Add approximation algorithms for traveling salesman problem (#4607)
- adds implementation of SNAP summarization algorithm (#4463)
- Update black (#4814)
- Restructure documentation (#4744)
- Pin upper bound on decorator for 2.6 release. (#4815)
- Use `callable()` to check if the object is callable (#1) (#4678)
- Remove dictionary from signature of tree_graph and tree_data (#4786)
- Make nx.hits a wrapper around different implementations, use scipy one by default (#4812)
- restructured networksimplex.py and added test_networksimplex.py (#4685)
- Update requirements (#4625)
- Fix Sphinx errors (#4817)
- Add topological_generations function (#4757)
- Add `initial_graph` parameter to simple and dual Barábasi-Albert random graphs (#4659)
- Link to guides (#4818)
- switch alias direction of spring_layout and fruchterman_reingold_layout (#4820)
- Fix to_undirected doc typo (#4821)
- Deprecate preserve_random_state (#4826)
- Fixes read/write_gml with nan/inf attributes (#4497)
- Remove pyyaml dependency via module getattr (#4802)
- Use pytest.approx (#4827)
- DOC: Clarify behaviour of k_crust(G, k) (#4831)
- Limit number of threads used by OMP in circleci. (#4830)
- Deprecate run (#4833)
- Fix a few broken links in the html docs (#4572)
- Refactor testing utilities (#4829)
- Fix edge drawing performance regression (#4825)
- Draft 2.6 release notes (#4828)
- Fix bad import pattern (#4839)
- Add info about testing and examples (#4582)
- Remove unused `normalized` parameter from communicability_betweenness_centrality (#4843)
- add special processing of `multigraph_input` upon graph init (#4823)
- Add dtype argument to adjacency_matrix (#4850)
- Use scipy to compute eigenvalues (#4847)
- Default to NumPy for simrank_similarity (#4841)
- Remove "networkx" from top-level networkx namespace (#4840)
- Designate 2.6rc1 release
- Bump release version
- DOC: point towards web archive link in GML docs (#4864)
- Fix docstring typo (#4871)
- Reformatted  table to address issue #4852 (#4875)
- spring_layout: ignore 'fixed' nodes not in the graph nodes (#4867)
- Deserializing custom default properties graph ml (#4872)
- DOC: Fix links, use DOI links, wayback machine where required (#4868)
- Fix conda instructions (#4884)
- Decode GraphML/yEd shape type (#4694)
- bugfix-for-issue-4353: modify default edge_id format (#4842)
- Raise ValueError if None is added as a node. (#4892)
- Update arrows default value in draw_networkx. (#4883)
- Doc/fix 403 error drawing custom icons (#4906)
- Remove decorator dependency (#4739)
- Update docstrings for dfs and bfs edges and fix cross links (#4900)
- Fix graph_class usage in to_undirected method (#4912)
- Fix assortativity coefficient calculation (#4851)
- Deprecate numeric_mixing_matrix. (#4923)
- Update read_gml docstring with destringizer ex (#4916)
- Update release process (#4866)
- Designate 2.6rc2 release
- Bump release version
- Add 3.0 migration guide (#4927)
- quotient_graph doc fix (#4930)
- Page number for Katz centrality reference (#4932)
- Expand destringizer example in read_gml docstring (#4925)
- move partition checking outside private _quotient_graph function (#4931)
- Fixes #4275 - Add comment to parallel betweenness example (#4926)
- Minor Improvements on Networkx/algorithms/community/quality.py (#4939)
- Fix numeric and degree assortativity coefficient calculation (#4928)
- fix spelling in docstring of conftest.py (#4945)
- fix trouble with init_cycle argument to two TSP functions (#4938)
- split out deprecation. remove all changes to neighbor_degree (#4937)
- Add matrix market to readwrite reference (#4934)
- fix typo for PR number of deprecation (#4949)
- Fix neighbor degree for directed graphs (#4948)
- `descendants_at_distance` also for non-DiGraphs (#4952)
- Changes to rst files to make doctests pass (#4947)
- Fix version pull down (#4954)
- Finalize 2.6 release notes (#4958)

Contributors
------------

- AbhayGoyal
- Suvayu Ali
- Alexandre Amory
- Francesco Andreuzzi
- Salim BELHADDAD
- Ross Barnowski
- Raffaele Basile
- Jeroen Bergmans
- R. Bernstein
- Geoff Boeing
- Kelly Boothby
- Jeff Bradberry
- Erik Brendel
- Justin Cai
- Thomas A Caswell
- Jonas Charfreitag
- Berlin Cho
- ChristopherReinartz
- Jon Crall
- Michael Dorner
- Harshal Dupare
- Andrew Eckart
- Tomohiro Endo
- Douglas Fenstermacher
- Martin Fleischmann
- Martha Frysztacki [frɨʂtat͡skʲ]
- Debargha Ganguly
- CUI Hao
- Floris Hermsen
- Ward Huang
- Elgun Jabrayilzade
- Han Jaeseung
- Mohammed Kashif
- Alex Korbonits
- Mario Kostelac
- Sebastiaan Lokhorst
- Lonnen
- Delille Louis
- Xiaoyan Lu
- Alex Malins
- Oleh Marshev
- Jordan Matelsky
- Fabio Mazza
- Chris McBride
- Abdulelah S. Al Mesfer
- Attila Mester
- Jarrod Millman
- Miroslav Šedivý
- Harsh Mishra
- S Murthy
- Matthias Nagel
- Attila Nagy
- Mehdi Nemati
- Dimitrios Papageorgiou
- Vitaliy Pozdnyakov
- Bharat Raghunathan
- Randy
- Michael Recachinas
- Carlos González Rotger
- Taxo Rubio
- Dan Schult
- Mridul Seth
- Kunal Shah
- Eric Sims
- Ludovic Stephan
- Justin Timmons
- Andrea Tomassilli
- Matthew Treinish
- Milo Trujillo
- Danylo Ulianych
- Alex Walker
- Stefan van der Walt
- Anthony Wilder Wohns
- Levi John Wolf
- Xiangyu Xu
- Shichu Zhu
- alexpsimone
- as1371
- cpurmessur
- dbxnr
- wim glenn
- goncaloasimoes
- happy
- jason-crowley
- jebogaert
- josch
- ldelille
- marcusjcrook
- guy rozenberg
- tom
- walkeralexander
