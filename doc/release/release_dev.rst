NetworkX 3.0 (unreleased)
=========================

Release date: TBD

Supports Python 3.8, 3.9, 3.10, and 3.11.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 4 months of work with over 217 pull requests by
37 contributors. We also have a :ref:`guide for people moving from NetworkX 2.X
to NetworkX 3.0 <migration_guide_from_2.x_to_3.0>`. Highlights include:

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
- We have added an experimental plugin feature which let users choose alternate
  backends like GraphBLAS, CuGraph for computation. This is an opt-in feature and
  may change in future releases.
- Improved integration with the general Scientific Python ecosystem: <link to
  the migration guide section?>

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

A total of 217 changes have been committed.

- Add 2.8.5 release notes
- update all_pairs_lca docstrings (#5876)
- Improve LCA input validation (#5877)
- strategy_saturation_largest_first now accepts partial colorings (#5888)
- Fixed unused root argument in has_bridges (#5846)
- Update docs to include description of the `return_seen` kwarg (#5891)
- Add cache reset for when G._node is changed (#5894)
- Add weight distance metrics (#5305)
- Allow classes to relabel nodes -- casting (#5903)
- Update lattice.py (#5914)
- docstring updates for `union`, `disjoint_union`, and `compose` (#5892)
- Adds ```nx.bfs_layers``` method (#5879)
- Add to about_us.rst (#5919)
- Update precommit hooks (#5923)
- Remove old Appveyor cruft (#5924)
- signature change for `node_link` functions: for issue #5787 (#5899)
- Allow unsortable nodes in approximation.treewidth functions (#5921)
- Fix Louvain_partitions by yielding a copy of the sets in the partition gh-5901 (#5902)
- Replace LCA with naive implementations (#5883)
- Add function bfs_layers to docs (#5932)
- Bump nodelink args deprecation expiration to v3.2 (#5933)
- Update mapping logic in `relabel_nodes` (#5912)
- Propose to make new node_link arguments keyword only. (#5928)
- docstring update to lexicographical_topological_sort issue 5681 (#5930)
- Update pygraphviz (#5934)
- See matplotlb 3.6rc1 failure (#5937)
- Further improvements to strategy_saturation_largest_first (#5935)
- Arf layout (#5910)
- [ENH] Find and verify a minimal D-separating set in DAG (#5898)
- Add Mehlhorn Steiner approximations (#5629)
- Updated networkx/classes/function.py . Solves Issue #5463 (#5474)
- Improved documentation for all_simple_paths (#5944)
- Change is_path to return False when node not in G instead of raising exception (#5943)
- Preliminary VF2++ Implementation (#5788)
- Minor docstring touchups and test refactor for `is_path` (#5967)
- Update documentation header links for latest pydata-sphinx-theme (#5966)
- Switch to relative import for vf2pp_helpers. (#5973)
- Add vf2pp_helpers subpackage to wheel (#5975)
- Enhance biconnected components to avoid indexing (#5974)
- Update mentored projects list (#5985)
- Add concurrency hook to cancel jobs on new push. (#5986)
- Make all.py generator friendly (#5984)
- Fix failing example due to mpl 3.6 colorbar. (#5994)
- Only run scheduled pytest-randomly job in main repo. (#5993)
- Fix steiner tree test (#5999)
- Add Tidelift security vulnerability link (#6001)
- Update linters (#6006)
- Update doc requirements (#6008)
- VF2++ for Directed Graphs (#5972)
- Fix defect and update docs for MappedQueue, related to gh-5681 (#5939)
- Fix warnings from running tests in randomized order (#6014)
- Update pydata-sphinx-theme (#6012)
- update security link to tidelift (#6019)
- Update numpydoc (#6022)
- Support Python 3.11 (#6023)
- Update linters (#6024)
- Fixed test for average shortest path in the case of directed graphs (#6003)
- Minor updates to expanders generator tests (#6027)
- Update deprecations after 3.0 dep sprint (#6031)
- Use scipy.sparse array datastructure (#6037)
- Designate 3.0b1 release
- Bump release version
- Use org funding.yml
- Add missing asserts to tests (#6039)
- improve test coverage for algorithms in load centrality (#6080)
- Improve test coverage expanders line graph generators solved (PR for issue #6034) (#6071)
- Update which flow functions support the cutoff argument (#6085)
- Update GML parsing/writing to allow empty lists/tuples as node attributes (#6093)
- Replace .A call with .toarray for sparse array in example. (#6106)
- Improve test coverage for algorithms/richclub.py (#6089)
- Tested boykov_kolmogorov and dinitz with cutoff (#6104)
- Improve test coverage for multigraph class (#6101)
- Improve test coverage for algorithms in dominating_set.py (PR for issue 6032) (#6068)
- Warn on unused visualization kwargs that only apply to FancyArrowPatch edges (#6098)
- Improve test coverage for graph class (#6105)
- Fix weighted MultiDiGraphs in DAG longest path algorithms + add additional tests (#5988)
- added coverage in generators/tree.py (#6082)
- DOC: Specifically branch off main, instead of current branch (#6127)
- Circular center node layout (#6114)
- Improve test coverage for multidigraph class (#6131)
- Improve test coverage for digraph class (#6130)
- Improve test coverage for algorithms in dispersion.py (#6100)
- Fix doc inconsistencies related to cutoff in connectivity.py and disjoint_paths.py (#6113)
- Remove deprecated maxcardinality parameter from min_weight_matching (#6146)
- Remove deprecated `find_cores` (#6139)
- Remove deprecated project function from bipartite package. (#6147)
- Test on Python 3.11 (#6159)
- Improve test coverage in algorithms shortest paths unweighted.py (#6121)
- Increased test coverage algorithms/matching.py (#6095)
- Renamed test functions in test_lowest_common_ancestors (#6110)
- Increase covering coverage (#6099)
- Add example for fiedler_vector (#6155)
- Improve test coverage for cycles.py (#6152)
- Added an example in all_pairs_node_connectivity  (#6126)
- Amount of nodes and edges have mistakes when reading adjlist file (#6132)
- Update pytest to v7.2 (#6165)
- Improve test coverage for voterank algorithm (#6161)
- plugin based backend infrastructure to use multiple computation backends (#6000)
- Undocumented parameters in dispersion (#6183)
- improve swap.py test coverage  (#6176)
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
- Add clear_edges() method to the list of methods to be frozen by nx.freeze() (#6190)
- Adds LCA test case for self-ancestors from gh-4458. (#6218)
- Minor Python 2 cleanup (#6219)
- Add example laplacian matrix  (#6168)
- Revert 6219 and delete comment. (#6222)
- fix wording in error message (#6228)
- Rm incorrect test case for connected edge swap (#6223)


Contributors
------------
Made by the following committers [alphabetical by last name]:

- 0ddoe_s
- Tanmay Aeron
- Guy Aglionby
- Douglas K. G. Araujo
- Ross Barnowski
- Paula Pérez Bianchi
- Kevin Brown
- DiamondJoseph
- Casper van Elteren
- Radoslav Fulek
- Juanita Gomez
- Michael Holtz
- Abangma Jessika
- Tigran Khachatryan
- Dhaval Kumar
- Adam Li
- Lucas H. McCabe
- Jarrod Millman
- Mjh9122
- Sultan Orazbayev
- Konstantinos Petridis
- Alimi Qudirah
- Adam Richardson
- Okite chimaobi Samuel
- Jefter Santiago
- Dan Schult
- Mridul Seth
- Tindi Sommers
- Morrison Turnansky
- Sebastiano Vigna
- George Watkins
- Isaac Western
- ddelange
- ladykkk
- nsengaw4c
- pmlpm1986
- stevenstrickler
