NetworkX 3.0
============

Release date: 7 January 2023

Supports Python 3.8, 3.9, 3.10, and 3.11.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 8 months of work with over 180 changes by
41 contributors. We also have a `guide for people moving from NetworkX 2.X
to NetworkX 3.0 <https://networkx.org/documentation/latest/release/migration_guide_from_2.x_to_3.0.html>`_. Highlights include:

- Better syncing between G._succ and G._adj for directed G.
  And slightly better speed from all the core adjacency data structures.
  G.adj is now a cached_property while still having the cache reset when
  G._adj is set to a new dict (which doesn't happen very often).
  Note: We have always assumed that G._succ and G._adj point to the same
  object. But we did not enforce it well. If you have somehow worked
  around our attempts and are relying on these private attributes being
  allowed to be different from each other due to loopholes in our previous
  code, you will have to look for other loopholes in our new code
  (or subclass DiGraph to explicitly allow this).
- If your code sets G._succ or G._adj to new dictionary-like objects, you no longer
  have to set them both. Setting either will ensure the other is set as well.
  And the cached_properties G.adj and G.succ will be rest accordingly too.
- If you use the presence of the attribute `_adj` as a criteria for the object
  being a Graph instance, that code may need updating. The graph classes
  themselves now have an attribute `_adj`. So, it is possible that whatever you
  are checking might be a class rather than an instance. We suggest you check
  for attribute `_adj` to verify it is like a NetworkX graph object or type and
  then `type(obj) is type` to check if it is a class.
- We have added an `experimental plugin feature <https://github.com/networkx/networkx/pull/6000>`_,
  which let users choose alternate backends like GraphBLAS, CuGraph for computation. This is an
  opt-in feature and may change in future releases.
- Improved integration with the general `Scientific Python ecosystem <https://networkx.org/documentation/latest/release/migration_guide_from_2.x_to_3.0.html#improved-integration-with-scientific-python>`_.
- New drawing feature (module and tests) from NetworkX graphs to the TikZ library of TeX/LaTeX.
  The basic interface is ``nx.to_latex(G, pos, **options)`` to construct a string of latex code or
  ``nx.write_latex(G, filename, as_document=True, **options)`` to write the string to a file.
- Added an improved subgraph isomorphism algorithm called VF2++.

Improvements
------------
- [`#5663 <https://github.com/networkx/networkx/pull/5663>`_]
  Implements edge swapping for directed graphs.
- [`#5883 <https://github.com/networkx/networkx/pull/5883>`_]
  Replace the implementation of ``lowest_common_ancestor`` and
  ``all_pairs_lowest_common_ancestor`` with a "naive" algorithm to fix
  several bugs and improve performance.
- [`#5912 <https://github.com/networkx/networkx/pull/5912>`_]
  The ``mapping`` argument of the ``relabel_nodes`` function can be either a
  mapping or a function that creates a mapping. ``relabel_nodes`` first checks
  whether the ``mapping`` is callable - if so, then it is used as a function.
  This fixes a bug related for ``mapping=str`` and may change the behavior for
  other ``mapping`` arguments that implement both ``__getitem__`` and
  ``__call__``.
- [`#5898 <https://github.com/networkx/networkx/pull/5898>`_]
  Implements computing and checking for minimal d-separators between two nodes.
  Also adds functionality to DAGs for computing v-structures.
- [`#5943 <https://github.com/networkx/networkx/pull/5943>`_]
  ``is_path`` used to raise a `KeyError` when the ``path`` argument contained
  a node that was not in the Graph. The behavior has been updated so that
  ``is_path`` returns `False` in this case rather than raising the exception.
- [`#6003 <https://github.com/networkx/networkx/pull/6003>`_]
  ``avg_shortest_path_length`` now raises an exception if the provided
  graph is directed but not strongly connected. The previous test (weak
  connecting) was wrong; in that case, the returned value was nonsensical.

API Changes
-----------

- [`#5813 <https://github.com/networkx/networkx/pull/5813>`_]
  OrderedGraph and other Ordered classes are replaced by Graph because
  Python dicts (and thus networkx graphs) now maintain order.
- [`#5899 <https://github.com/networkx/networkx/pull/5899>`_]
  The `attrs` keyword argument will be replaced with keyword only arguments
  `source`, `target`, `name`, `key` and `link` for `json_graph/node_link` functions.

Deprecations
------------

- [`#5723 <https://github.com/networkx/networkx/issues/5723>`_]
  ``nx.nx_pydot.*`` will be deprecated in the future if pydot isn't being
  actively maintained. Users are recommended to use pygraphviz instead. 
- [`#5899 <https://github.com/networkx/networkx/pull/5899>`_]
  The `attrs` keyword argument will be replaced with keyword only arguments
  `source`, `target`, `name`, `key` and `link` for `json_graph/node_link` functions.

Merged PRs
----------

- Bump release version
- Add characteristic polynomial example to polynomials docs (#5730)
- Remove deprecated function is_string_like (#5738)
- Remove deprecated function make_str (#5739)
- Remove unused 'name' parameter from `union` (#5741)
- Remove deprecated function is_iterator (#5740)
- Remove deprecated `euclidean` from geometric.py (#5744)
- Remove deprecated function utils.consume (#5745)
- Rm `to_numpy_recarray` (#5737)
- Remove deprecated function utils.empty_generator (#5748)
- Rm jit.py (#5751)
- Remove deprecated context managers (#5752)
- Remove deprecated function utils.to_tuple (#5755)
- Remove deprecated display_pygraphviz (#5754)
- Remove to_numpy_matrix & from_numpy_matrix (#5746)
- Remove deprecated decorator preserve_random_state (#5768)
- Remove deprecated function is_list_of_ints (#5743)
- Remove decorator random_state (#5770)
- remove `adj_matrix` from `linalg/graphmatrix.py` (#5753)
- Remove betweenness_centrality_source (#5786)
- Remove deprecated simrank_similarity_numpy (#5783)
- Remove networkx.testing subpackage (#5782)
- Change PyDot PendingDeprecation to Deprecation (#5781)
- Remove deprecated numeric_mixing_matrix (#5777)
- Remove deprecated functions make_small_graph and make_small_undirected_graph (#5761)
- Remove _naive_greedy_modularity_communities (#5760)
- Make chordal_graph_cliques a generator (#5758)
- update cytoscape functions to drop old signature (#5784)
- Remove deprecated functions dict_to_numpy_array2 and dict_to_numpy_array1 (#5756)
- Remove deprecated function utils.default_opener (#5747)
- Remove deprecated function iterable (#5742)
- remove old attr keyword from json_graph/tree (#5785)
- Remove generate_unique_node (#5780)
- Replace node_classification subpackage with a module (#5774)
- Remove gpickle (#5773)
- Remove deprecated function extrema_bounding (#5757)
- Remove coverage and performance from quality (#5775)
- Update return type of google_matrix to numpy.ndarray (#5762)
- Remove deprecated k-nearest-neighbors (#5769)
- Remove gdal dependency (#5766)
- Update return type of attrmatrix (#5764)
- Remove unused deprecated argument from to_pandas_edgelist (#5778)
- Remove deprecated function edge_betweenness (#5765)
- Remove pyyaml dependency (#5763)
- Remove copy methods for Filter* coreviews (#5776)
- Remove deprecated function nx.info (#5759)
- Remove deprecated n_communities argument from greedy_modularity_communities (#5789)
- Remove deprecated functions hub_matrix and authority_matrix (#5767)
- Make HITS numpy and scipy private functions (#5771)
- Add Triad example plot (#5528)
- Add gallery example visualizing DAG with multiple layouts (#5432)
- Make pagerank numpy and scipy private functions (#5772)
- Implement directed edge swap (#5663)
- Update relabel.py to preserve node order (#5258)
- Modify DAG example to show topological layout. (#5835)
- Add docstring example for self-ancestors/descendants (#5802)
- Update precommit linters (#5839)
- remove to/from_scipy_sparse_matrix (#5779)
- Clean up from PR #5779 (#5841)
- Corona Product (#5223)
- Add direct link to github networkx org sponsorship (#5843)
- added examples to efficiency_measures.py (#5643)
- added examples to regular.py (#5642)
- added examples to degree_alg.py (#5644)
- Add docstring examples for triads functions (#5522)
- Fix docbuild warnings: is_string_like is removed and indentation in corona product (#5845)
- Use py_random_state to control randomness of random_triad (#5847)
- Remove OrderedGraphs (#5813)
- Drop NumPy 1.19 (#5856)
- Speed up unionfind a bit by not adding root node in the path (#5844)
- Minor doc fixups (#5868)
- Attempt to reverse slowdown from hasattr  needed for cached_property (#5836)
- make lazy_import private and remove its internal use (#5878)
- strategy_saturation_largest_first now accepts partial colorings (#5888)
- Add weight distance metrics (#5305)
- docstring updates for `union`, `disjoint_union`, and `compose` (#5892)
- Update precommit hooks (#5923)
- Remove old Appveyor cruft (#5924)
- signature change for `node_link` functions: for issue #5787 (#5899)
- Replace LCA with naive implementations (#5883)
- Bump nodelink args deprecation expiration to v3.2 (#5933)
- Update mapping logic in `relabel_nodes` (#5912)
- Update pygraphviz (#5934)
- Further improvements to strategy_saturation_largest_first (#5935)
- Arf layout (#5910)
- [ENH] Find and verify a minimal D-separating set in DAG (#5898)
- Add Mehlhorn Steiner approximations (#5629)
- Preliminary VF2++ Implementation (#5788)
- Minor docstring touchups and test refactor for `is_path` (#5967)
- Switch to relative import for vf2pp_helpers. (#5973)
- Add vf2pp_helpers subpackage to wheel (#5975)
- Enhance biconnected components to avoid indexing (#5974)
- Update mentored projects list (#5985)
- Add concurrency hook to cancel jobs on new push. (#5986)
- Make all.py generator friendly (#5984)
- Only run scheduled pytest-randomly job in main repo. (#5993)
- Fix steiner tree test (#5999)
- Update doc requirements (#6008)
- VF2++ for Directed Graphs (#5972)
- Fix defect and update docs for MappedQueue, related to gh-5681 (#5939)
- Update pydata-sphinx-theme (#6012)
- Update numpydoc (#6022)
- Fixed test for average shortest path in the case of directed graphs (#6003)
- Update deprecations after 3.0 dep sprint (#6031)
- Use scipy.sparse array datastructure (#6037)
- Designate 3.0b1 release
- Bump release version
- Use org funding.yml
- Update which flow functions support the cutoff argument (#6085)
- Update GML parsing/writing to allow empty lists/tuples as node attributes (#6093)
- Warn on unused visualization kwargs that only apply to FancyArrowPatch edges (#6098)
- Fix weighted MultiDiGraphs in DAG longest path algorithms + add additional tests (#5988)
- Circular center node layout (#6114)
- Fix doc inconsistencies related to cutoff in connectivity.py and disjoint_paths.py (#6113)
- Remove deprecated maxcardinality parameter from min_weight_matching (#6146)
- Remove deprecated `find_cores` (#6139)
- Remove deprecated project function from bipartite package. (#6147)
- Improve test coverage for voterank algorithm (#6161)
- plugin based backend infrastructure to use multiple computation backends (#6000)
- Undocumented parameters in dispersion (#6183)
- Swap.py coverage to 100 (#6176)
- Improve test coverage for current_flow_betweenness module (#6143)
- Completed Testing in community.py resolves issue #6184 (#6185)
- Added an example to algebraic_connectivity (#6153)
- Add ThinGraph example to Multi*Graph doc_strings (#6160)
- Fix defect in eulerize, replace reciprocal edge weights (#6145)
- For issue #6030 Add test coverage for algorithms in beamsearch.py (#6087)
- Improve test coverage expanders stochastic graph generators (#6073)
- Update developer requirements  (#6194)
- Designate 3.0rc1 release
- Bump release version
- Tests added in test_centrality.py (#6200)
- add laplacian_spectrum example (#6169)
- PR for issue #6033 Improve test coverage for algorithms in betweenness_subset.py #6033 (#6083)
- Di graph edges doc fix (#6108)
- Improve coverage for core.py (#6116)
- Add clear edges method as a method to be frozen by nx.freeze (#6190)
- Adds LCA test case for self-ancestors from gh-4458. (#6218)
- Minor Python 2 cleanup (#6219)
- Add example laplacian matrix  (#6168)
- Revert 6219 and delete comment. (#6222)
- fix wording in error message (#6228)
- Rm incorrect test case for connected edge swap (#6223)
- add missing `seed` to function called by `connected_double_edge_swap` (#6231)
- Hide edges with a weight of None in A*. (#5945)
- Add dfs_labeled_edges reporting of reverse edges due to depth_limit. (#6240)
- Warn users about duplicate nodes in generator function input (#6237)
- Re-enable geospatial examples (#6252)
- Draft 3.0 release notes (#6232)
- Add 2.8.x release notes (#6255)
- doc: clarify allowed `alpha` when using nx.draw_networkx_edges (#6254)
- Add a contributor (#6256)
- Allow MultiDiGraphs for LCA (#6234)
- Update simple_paths.py to improve readability of the BFS. (#6273)
- doc: update documentation when providing an iterator over current graph to add/remove_edges_from. (#6268)
- Fix bug vf2pp is isomorphic issue 6257 (#6270)
- Improve test coverage for Eigenvector centrality  (#6227)
- Bug fix in swap: directed_edge_swap and double_edge_swap  (#6149)
- Adding a test to verify that a NetworkXError is raised when calling n… (#6265)
- Pin to sphinx 5.2.3 (#6277)
- Update pre-commit hooks (#6278)
- Update GH actions (#6280)
- Fix links in release notes (#6281)
- bug fix in smallworld.py: random_reference and lattice_reference (#6151)
- [DOC] Follow numpydoc standard in barbell_graph documentation (#6286)
- Update simple_paths.py: consistent behaviour for `is_simple_path` when path contains nodes not in the graph. (#6272)
- Correctly point towards 2.8.8 in release notes (#6298)
- Isomorphism improve documentation (#6295)
- Improvements and test coverage for `line.py` (#6215)
- Fix typo in Katz centrality comment (#6310)
- Broken link in isomorphism documentation (#6296)
- Update copyright years to 2023 (#6322)
- fix warnings for make doctest (#6323)
- fix whitespace issue in test_internet_as_graph (#6324)
- Create a Tikz latex drawing feature for networkx (#6238)
- Fix docstrings (#6329)
- Fix documentation deployment (#6330)
- Fix links to migration guide (#6331)
- Fix links to migration guide (#6331)
- Fix typo in readme file (#6312)
- Fix typos in the networkx codebase (#6335)
- Refactor vf2pp modules and test files (#6334)

Contributors
------------

- 0ddoe_s
- Abangma Jessika
- Adam Li
- Adam Richardson
- Ali Faraji
- Alimi Qudirah
- Anurag Bhat
- Ben Heil
- Brian Hou
- Casper van Elteren
- danieleades
- Dan Schult
- ddelange
- Dilara Tekinoglu
- Dimitrios Papageorgiou
- Douglas K. G. Araujo
- Erik Welch
- George Watkins
- Guy Aglionby
- Isaac Western
- Jarrod Millman
- Jim Kitchen
- Juanita Gomez
- Kevin Brown
- Konstantinos Petridis
- ladykkk
- Lucas H. McCabe
- Ludovic Stephan
- Lukong123
- Matt Schwennesen
- Michael Holtz
- Morrison Turnansky
- Mridul Seth
- nsengaw4c
- Okite chimaobi Samuel
- Paula Pérez Bianchi
- Radoslav Fulek
- reneechebbo
- Ross Barnowski
- Sebastiano Vigna
- stevenstrickler
- Sultan Orazbayev
- Tina Oberoi
