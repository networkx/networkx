NetworkX 2.8.8
==============

Release date: 2 November 2022

Supports Python 3.8, 3.9, 3.10 and 3.11.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our :ref:`gallery of examples <examples_gallery>`.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

- [`#5972 <https://github.com/networkx/networkx/pull/5972>`_]
  Added VF2++ isomorphism algorithm for directed graphs.

Merged PRs
----------

A total of 33 changes have been committed.

- Update doc requirements (#6008)
- VF2++ for Directed Graphs (#5972)
- Fix defect and update docs for MappedQueue, related to gh-5681 (#5939)
- Fix warnings from running tests in randomized order (#6014)
- Update pydata-sphinx-theme (#6012)
- update secutiry link to tidelift (#6019)
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
- fixes #6036 (#6080)
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
- Update pytest (#6165)

Contributors
------------

- Douglas K. G. Araujo
- Ross Barnowski
- Paula Pérez Bianchi
- Kevin Brown
- DiamondJoseph
- Jarrod Millman
- Mjh9122
- Konstantinos Petridis
- Alimi Qudirah
- Okite chimaobi Samuel
- Jefter Santiago
- Dan Schult
- Mridul Seth
- Tindi Sommers
- Sebastiano Vigna
- stevenstrickler
