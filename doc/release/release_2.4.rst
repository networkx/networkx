Announcement: NetworkX 2.4
==========================

We're happy to announce the release of NetworkX 2.4!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 6 months of work with over 200 commits by
67 contributors. Highlights include:

- Remove deprecated code from 1.x
- Support for Python 3.8
- Switched to pytest for testing
- Last release to support Python 3.5

New Functions:

- barycenter functions
- Bethe Hessian matrix function
- Eulerian Path methods
- group centrality measures
- subgraph monomorphisms
- k-truss algorithms
- onion decomposition
- resistance distance
- asteroidal triples
- non-randomness measures
- linear prufing
- minimum weight bipartite matching
- Incremental closeness centrality
- ISMAGS subgraph isomorphism algorithm
- create chordal graph of a graph

New generators

- Binomial tree generator
- Directed joint degree generator
- Random internet AS graph generator

New for Layouts

- spiral node layout routine
- support for 3d layouts


Improvements
------------
- allow average shortest path to use Floyd-Warshall method
- improve read/write of GML, GEXF, GraphML
- allow string or json object as input to jit_graph
- attempt to allow numpy.array input in place of lists in more places
- faster strongly connected components
- faster Floyd-Warshall Optimization
- faster global efficiency
- faster transitive closure
- fix unionfind; betweenness_subset; lexico-topo-sort; A*;
  inverse_line_graph; async label propagation; edgelist reading;
  Gomory-Hu flow method; label_propagation; partial_duplication;
  shell_layout with 1 node in shell; from_pandas_edgelist  
- Documentation improvement and fixes


API Changes
-----------

A utility function is_list_of_ints became is_bunch_of_ints
and now tests int(item)==item instead of isinstance(_, int)
This allows e.g. floats whose values are integer.

Added utility make_list_of_ints to convert containers of
integer values to lists of integers


Deprecations
------------

Removed functions (marked as deprecated in NetworkX 2.1):

- attracting_component_subgraphs
- connected_component_subgraphs
- weakly_connected_component_subgraphs
- strongly_connected_component_subgraphs
- biconnected_component_subgraphs
- See docs for component functions for how to get subgraphs.

Graph Object methods removed (marked as deprecated 2.1)

- G.add_path
- G.add_cycle
- G.add_star
- G.nodes_with_selfloops
- G.number_of_selfloops
- G.selfloop_edges
- These are now NetworkX functions, e.g. nx.add_star(G, 5)
- G.node   --> use G.nodes
- G.fresh_copy   --> use G.__class__

Remove old names for graphview functions.

- ReverseView
- SubGraph
- SubMultiGraph
- SubMultiDiGraph
- SubDiGraph
- GraphView
- DiGraphView
- MultiGraphView
- MultiDiGraphView
- MultiReverseView
- Use reverse_view, subgraph_view and generic_graph_view.

Pull requests and commits merged in this release
------------------------------------------------

A total of 205 changes have been committed.

- Bump release version
- algorithms/traversal/edgebfs name fix (#3397)
- Add see also links (#3403)
- Add the reference for the Harary graph generators (#3407)
- typo: swap source and target (#3413)
- Fix spring_layout bug with fixed nodes (#3415)
- Move LFR_benchmark to generators (#3411)
- Add barycenter algorithm (#2939)
- Add bethe hessian matrix (#3401)
- Binomial trees generator (#3409)
- Fix edge_color inconsistency with node_color and description. (#3395)
- Adding module for group centrality measures (#3421)
- Improve edgelist See Also (#3423)
- Typo fix (#3424)
- Add doc warning about self-loops for adamic_adar_index (#3427)
- Fix UnionFind set extraction (#3224)
- add required argument to `write_graphml` example (#3429)
- Fix centrality betweeness subset (#3425)
- Add two versions of Simrank similarity (#3222)
- Fixed typo
- Merge pull request #3436 from nandahkrishna/fix-typo-betweenness-centrality-subset-test
- Reorder and complete doc (#3438)
- added topo_order parameter to functions that rely on topological_sort (#3447)
- Implemented subgraph monomorphism (#3435)
- Set seed in random_degree_sequence_graph docstring test (#3451)
- Replace cb.iterable with np.iterable (#3458)
- don't remove ticks of other pyplot axes (#3476)
- Fix typo in "G>raph Modelling Language" (#3468)
- Naive k-truss algorithm implementation. (#3462)
- Adding onion decomposition (#3461)
- New Feature - Resistance Distance (#3385)
- No multigraphs for betweenness (#3454)
- Wheels are python 3 only
- Fix deprecation warning with Python 3.7 (#3487)
- Fix dfs_preorder_nodes docstring saying "edges" instead of "nodes" (#3484)
- Added group closeness and group degree centralities (#3437)
- Fixed incorrect docs (#3495)
- Fixes Issue #3493 - Bug in lexicographical_topological_sort() (#3494)
- AT-free graph recognition (#3377)
- Update introduction.rst (#3504)
- Full join operation and cograph generator (#3503)
- Optimize the strongly connected components algorithm. (#3516)
- Adding non-randomness measures for graphs (#3515)
- Added safeguards (input graph G) for non-randomness measures  (#3526)
- Optimize the strongly connected components algorithm - Take 2 (#3519)
- Small fix for bug found @ issue #3524 (#3529)
- Restore checking PyPy3 (#3514)
- Linear prufer coding (#3535)
- Fix inverse_line_graph. (#3507)
- Fix A* returning wrong solution (#3508)
- Implement minimum weight full matching of bipartite graphs (#3527)
- Get chordal graph for #1054 (#3353)
- Faster transitive closure computation for DAGs (#3445)
- Write mixed-type attributes correctly in write_graphml_lxml (#3536)
- Fixes some edge cases for inverse_line_graph(). (#3538)
- explicitly stated i.j convention in to_numpy_array
- Incremental Closeness Centrality (undirected, unweighted graphs) (#3444)
- Implement ISMAGS subgraph isomorphism algorithm (#3312)
- Fixes bug in networkx.algorithms.community.label_propagation.asyn_lpa_communities (#3545)
- When exporting to GML, write non 32-bit numbers as strings. (#3540)
- Try to bug Fix #3552 (#3554)
- add Directed Joint Degree Graph generator (#3551)
- typo (#3557)
- Fix a few documentation issues for the bipartite algorithm reference (#3555)
- i,j convention in adj mat i/o in relevant funcs
- Merge pull request #3542 from malch2/doc/update
- Add 3.8-dev to travis
- Fix dict iteration for Py3.8
- Ignore other failures for now
- Fix a typo in docstring for get_edge_data (#3564)
- Fix wrong title (#3566)
- Fix typo in doctring (#3568)
- Fix and Improve docstrings in graph.py (#3569)
- Improved graph class selection table (#3570)
- Add spiral layout for graph drawing (#3534)
- #3575 return coordinates of 3d layouts (#3576)
- Handle k==n within the Watts-Strogatz graph generator (#3579)
- Floyd-Warshall Optimization (#3400)
- Use Sphinx 2.2
- Add missing link to asteroidal docs
- Fix Sphinx warnings
- Fix Sphinx latexpdf build
- Updated Contributor list (#3592)
- Prim from list to set (#3512)
- Fix issue 3491 (#3588)
- Make Travis fail on Python 3.8 failures
- Fix test_gexf to handle default serialisation order of the XML attributes
- Remove future imports needed by Py2
- add internet_as_graph generator (#3574)
- remove cyclical references from OutEdgeDataView (#3598)
- Add minimum source and target margin to draw_networkx_edges. (#3390)
- fix to_directed function (#3599)
- Fixes #3573:GEXF output problem (#3606)
- Global efficiency attempt to speed up (#3604)
- Bugfix: Added flexibility in reading values for label and id (#3603)
- Add method floyd-warshall to average_shortest_path_length (#3267)
- Replaced is with == and minor pycodestyle fixes (#3608)
- Fix many documentation based Issues (#3609)
- Resolve many documentation issues (#3611)
- Fixes #3187  transitive_closure now returns self-loops when cycles present (#3613)
- Add support for initializing pagerank_scipy (#3183)
- Add last 7 lines of Gomory-hu algorithm Fixes #3293 (#3614)
- Implemented Euler Path functions (#3399)
- Fix the direction of edges in label_propagation.py (#3619)
- Removed unused import of random module (#3620)
- Fix operation order in partial_duplication_graph (#3626)
- Keep shells with 1 node away from origin in shell_layout (#3629)
- Allow jit_graph to read json string or json object (#3628)
- Fix typo within incode documentation (#3621)
- pycodestyle and update docs for greedy_coloring.py+tests (#3631)
- Add version badges
- Load long description from README
- Add missing code block (#3630)
- Change is_list_of_ints to make_list_of_ints (#3617)
- Handle edgeattr in from_pandas_edgelist when no columns match request (#3634)
- Make draft of release notes for v2.4
- Shift notes from dev to v2.4 filename.
- Use recent pypy
- Test Py 3.8 on macos
- add check of attr type before converting inf/nan in GEXF (#3636)
- Fix sphinx errors And add links to single_source_dijkstra in docs for dijkstra_path/length (#3638)
- Document subgraph_view (#3627)
- First round of pytest fixes
- Use class methods for class setup/teardown
- Have CIs use pytest
- Use class methods for class setup/teardown, cont.
- Do less testing (until we get it working)
- replace idiom from networkx import * in test files
- Fix assert funcs override
- Fix static methods in link_prediction
- Partially fix v2userfunc tests
- Fix graph/digraph tests
- Fix multigraph checks
- Fix multidigraph checks
- Fix test_function checks
- Fix distance_measures tests
- Fix decorators tests
- Fix some raises in test_mst
- Fix clique tests
- Fix yaml tests
- Fix tests in reportviews
- Fix vf2 tests
- Fix mst tests
- Fix gdal tests
- Convert nose.tools.assert_* functions into asserts
- Remove unused imports
- Fix some warnings
- Update testing instructions
- Reenable all test platforms
- Fix some __init__ warnings
- replace nose yield tests in test_coloring.py
- Add testing, coverage, and dev environment info
- Try pytestimportorskip
- Another pair of variations on pytest.importorskip
- fix typo and try again
- Remove deprecated weakly_connected_component_subgraphs
- replace assert_almost_equal and raises in algorithms/tests
- set places=0 on tests that use old almost_equal
- Update nx.test()
- Have pytest run doctests / not sphinx
- Revert "Remove deprecated weakly_connected_component_subgraphs"
- remove warnings for using deprecated function
- Remove deprecated functions and methods. add to release notes.
- Fix subgraph_view testing
- remove tests of deprecated views and fix use of deprecated G.node
- tracking down use of deprecated functions
- Fix deprecated use of add_path/star/cycle
- reduce warnings for deprecated functions
- skirt issues wih raises in test_harmonic
- reduce the number of warnings by removing deprecated functions
- convert_matrix demo of one way to get doctests to work
- Remove deprecated from examples
- Changes to convert_matrix and others that depend on np.matrix
- clean up doctest deprecated code
- More doctest corrections
- Fix examples
- Remove nose from generators
- Remove nose from utils
- Remove nose from classes
- Replace nose.assert_raises with pytest.raises
- Replace nose.raises with pytest.raises context manager
- Replace `eq_`, `ok_` with assert
- Use pytest for doctest
- Highlight switch to pytest in release notes
- Remove `from nose.tools import *`
- Remove nose.tools.SkipTest
- Finalize transition to pytest
- Merge pull request #3639 from stefanv/pytest-port
- Test Python 3.8 with AppVeyor
- Merge pull request #3648 from jarrodmillman/windows-py3.8
- Remove deprecated weakly_connected_component_subgraphs
- Update release notes
- Update README
- Announce Python 3.8 support
- Designate 2.4rc1 release
- Bump release version
- Remove remaining SkipTests
- fix documentation notes (#3644) (#3645)
- Test Py 3.8.0 on AppVeyor
- Speed up AppVeyor
- Cleanup travis config
- Improve CI caching
- Update Py 3.8 on travis
- Merge pull request #3652 from jarrodmillman/speedup-appveyor
- Finalize release notes

It contained the following 5 merges:

- Fixed typo in betweenness centrality subset test (#3436)
- explicitly stated i.j convention in to_numpy_array (#3542)
- pytest port (#3639)
- Test Python 3.8 with AppVeyor (#3648)
- Cleanup and speedup CI (#3652)

Contributors to this release
----------------------------

- Rajendra Adhikari
- Antoine Allard
- Antoine
- Salim BELHADDAD
- Luca Baldesi
- Tamás Bitai
- Tobias Blass
- Malayaja Chutani
- Peter Cock
- Almog Cohen
- Diogo Cruz
- Martin Darmüntzel
- Elan Ernest
- Jacob Jona Fahlenkamp
- Michael Fedell
- Andy Garfield
- Ramiro Gómez
- Haakon
- Alex Henrie
- Steffen Hirschmann
- Martin James McHugh III
- Jacob
- Søren Fuglede Jørgensen
- Omer Katz
- Julien Klaus
- Matej Klemen
- Nanda H Krishna
- Peter C Kroon
- Anthony Labarre
- Anton Lodder
- MCer4294967296
- Eric Ma
- Fil Menczer
- Erwan Le Merrer
- Alexander Metz
- Jarrod Millman
- Subhendu Ranajn Mishra
- Jamie Morton
- James Myatt
- Kevin Newman
- Aaron Opfer
- Aditya Pal
- Pascal-Ortiz
- Peter
- Jose Pinilla
- Alexios Polyzos
- Michael Recachinas
- Efraim Rodrigues
- Adam Rosenthal
- Dan Schult
- William Schwartz
- Weisheng Si
- Kanishk Tantia
- Ivan Tham
- George Valkanas
- Stefan van der Walt
- Hsi-Hsuan Wu
- Haochen Wu
- Xiangyu Xu
- Jean-Gabriel Young
- bkief
- daniel-karl
- michelb7398
- mikedeltalima
- nandahkrishna
- skhiuk
- tbalint
