NetworkX 2.5
============

Release date: 22 August 2020

Supports Python 3.6, 3.7, and 3.8.

NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <https://networkx.org/>`_
and our `gallery of examples
<https://networkx.org/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of 10 months of work with over 200 commits by
92 contributors. Highlights include:

- Dropped support for Python 3.5.
- add Pathlib support to work with files.
- improve performance.
- Updated docs and tests.
- Removed code designed to work with Python 2.

New Functions:

- lukes_partitioning
- triadic analysis functions
- functions for trophic levels analysis
- d_separated
- is_regular and other regular graph measures
- graph_hash using Weisfeiler Lehman methods
- common_neighbor_centrality (CCPA link prediction)
- max_weight_clique
- path_weight and is_path
- rescale_layout_dict
- junction_tree

New generators:

- paley_graph
- interval_graph

New layouts:

- multipartite_layout


Improvements
------------

- Add governance documents, developer guide and community structures
- Implement explicit deprecation policy.
- Initiate an NX Enhancement Proposal (NXEP) system
- optimize single_source_shortest_path
- improved consistent "weight" specification in shortest_path routines
- Reduce numpy.matrix usage which is discouraged by numpy.
- improved line color
- better search engine treatment of docs
- lattice and grid_graph and grid_2d_graph can use dim=tuple
- fix initializer of kamada_kawai_layout algorithm
- moral and threshold functions now included in namespace and docs
- scale arrows better when drawing
- more uniform creation of random lobster graphs
- allow editing graph during iteration over connected_components
- better column handling in coversion of pandas DataFrame
- allow simrank_similarity with directed graph input
- ensure VoteRank ability is nonnegative
- speedup kernighan_lin_bisection
- speedup negative weight cycle detection
- tree_isomorphism
- rooted_tree_isomorphism
- Gexf edge attribute "label" is available


API Changes
-----------

- enabled "copy" flag parameter in `contracted_nodes`
- allow partially periodic lattices
- return value for minimum_st_node_cut now always a set
- removed unused "has_numpy" argument from create_py_random_state
- fixed return values when drawing empty nodes and edges
- allow sets and frozensets of edges as input to nx.Graph()
- "weight" can be function for astar, directional_dijksta, all_shortest_path
- allow named key ids for GraphML edge writing
- all keywords are now checked for validity in nx.draw and friends
- EdgeDataView "in" operator checks if nodes are "in nbunch"
- remove completeness condition from minimum weight full matching
- option to sort neighbors in bfs traversal
- draw_networkx accepts numpy array for edgelist
- relabel_nodes with 2 nodes mapped to same node can now create multiedge
- steiner_tree works with MultiGraph
- Add `show` kwarg to view_pygraphviz (#4155)
- Prepare for turning chordal_graph_cliques into a generator (#4162)
- GraphML reader keyword force_multigraph creates MultiGraph even w/o multiedges


Deprecations
------------

- [`#3680 <https://github.com/networkx/networkx/pull/3680>`_]
  Deprecate `make_str(x)` for `str(x)`.
  Deprecate `is_string_like(obj)` for `isinstance(obj, str)`.

- [`#3725 <https://github.com/networkx/networkx/pull/3725>`_]
  Deprecate `literal_stringizer` and `literal_destringizer`.

- [`#3983 <https://github.com/networkx/networkx/pull/3983>`_]
  Deprecate `reversed` context manager.

- [`#4155 <https://github.com/networkx/networkx/pull/4155>`_]
  Deprecate `display_pygraphviz`.

- [`#4162 <https://github.com/networkx/networkx/pull/4162>`_]
  Deprecate `chordal_graph_cliques` returning a set.

- [`#4161 <https://github.com/networkx/networkx/pull/4161>`_]
  Deprecate `betweenness_centrality_source`.

- [`#4161 <https://github.com/networkx/networkx/pull/4161>`_]
  Deprecate `edge_betweeness`.

- [`#4161 <https://github.com/networkx/networkx/pull/4161>`_]
  Rename `_naive_greedy_modularity_communities` as `naive_greedy_modularity_communities`.

Merged PRs
----------

A total of 256 changes have been committed.

- Bump release version
- Update release process
- Drop support for Python 3.5
- fix typo docs
- Remove old Python 2 code
- Enable more doctests
- Fix pydot tests
- Unclear how to test the test helper function
- Pathlib introduced in Py 3.4
- Remove code using sys.version_info to detect Python 2
- Use yield from
- PEP8 fixes to tests
- Remove unused imports
- Use pytest.importorskip
- PEP8 fixes
- Remove unused imports
- Add pep8_speaks conf
- Use itertools accumulate
- Fixes issue 3610: Bug in version attribute of gexf.py
- Ignore W503
- Run doctest without optional dependencies
- Skip doctests when missing dependencies
- Remove sed imports
- Enable tests (#3678)
- `contracted_nodes` copy flag added (#3646)
- Deprecate make_str
- Deprecate is_string_like
- Fix PEP8 issues
- Enable ThinGraph tests (#3681)
- Optimize _single_shortest_path_length (#3647)
- Fix issue 3431: Return error in case of bad input to make_small_graph (#3676)
- avoid duplicate tests due to imports (#3684)
- Fix typo: Laplacion -> Laplacian (#3689)
- Add tests
- Lukes algorithm implementation (#3666)
- Remove shim that worked around using starmap
- Add back to gallery
- Add colormap and color limits to LineCollection (#3698)
- Fix matplotlib deprecation (#3697)
- Adapt SciPy CoC
- Update docs to be more accurate about speed of G.neighbors (#3699)
- Use canonical url to help search engines
- Remove duplicate license parameter (#3710)
- Fix documentation issues for exceptions in a few places
- Fix more documentation issues with exceptions
- Remove old Python 2 code
- Remove boiler plate from top of modules
- Remove superfluous encoding information
- Update examples
- Simplify package docstring
- Remove shebang from non-executables
- Add contributors
- K-truss is defined for edges being in (k-2) triangles and not for k triangles (#3713)
- Enable optional tests on Python 3.8
- Fix test_numpy_type to pass under Python 3.8
- Add links to data files
- Deprecate Python 2/3 compatibility code
- Update style
- Update style
- Separate easy and hard to install optional requirements
- Install optional dependencies by default
- Refactor tests
- Sample code for subgraph copy: add parenthesis to is_multigraph (#3734)
- Fixed typo (#3735)
- fix citation links (#3741)
- remove f strings from setup.py for clear error message < py3.6 (#3738)
- 3511 gml list support (#3649)
- added linestyle as argument (#3747)
- Link to files needed for example (#3752)
- fixed a typo
- Merge pull request #3759 from yohm/patch-1
- remove unused variable so grid_graph supports dim=tuple (#3760)
- Sudoku generator issue 3756 (#3757)
- Fix scaling of single node shells in shall_layout (#3764)
- Adding triadic analysis functions (#3742)
- Improve test coverage
- Update contribs script
- Convert %-format to fstring
- Upgrade to Py36 syntax
- Upgrade to Py36 syntax
- Update string format
- Fix scipy deprecation warnings
- Update year
- Silence known warnings (#3770)
- Fix docstring for asyn_fluidc (#3779)
- Fix #3703 (#3784)
- fix initializer for kamada_kawai_layout (networkx #3658) (#3782)
- Minor comments issue (#3787)
- Adding moral and threshold packages to main namespace (#3788)
- Add weight functions to bidirectional_dijkstra and astar (#3799)
- Shrink the source side of an arrow properly when drawing a directed edge. #3805 (#3806)
- option for partially-periodic lattices (networkx #3586) (#3807)
- Prevent KeyError on subgraph_is_monomorphic (#3798)
- Trophic Levels #3736 (#3804)
- UnionFind's union doesn't accurately track set sizes (#3810)
- Remove whitespace (#3816)
- reconsider the lobster generator (#3822)
- Fix typo (#3838)
- fix typo slightly confusing the meaning (#3840)
- Added fix for issue #3846 (#3848)
- Remove unused variable has_numpy from create_py_random_state (#3852)
- Fix return values when drawing empty nodes and edges  #3833 (#3854)
- Make connected_components safe to component set mutation (#3859)
- Fix example in docstring (#3866)
- Update README.rst website link to https (#3888)
- typo (#3894)
- Made CONTRIBUTING.rst more clearer (#3895)
- Fixing docs for nx.info(), along with necessary tests (#3893)
- added default arg for json dumps for jit_data func (#3891)
- Fixed nx.Digraph to nx.DiGraph (#3909)
- Use Sphinx 3.0.1
- Fix Sphinx deprecation
- Add logo to docs
- allow set of edge nodes (#3907)
- Add extra information when casting 'id' to int() fails. (Resolves #3910) (#3916)
- add paley graph (#3900)
- add paley graph to doc (#3927)
- Update astar.py (#3947)
- use keywords for positional arguments (#3952)
- fix documentation (#3959)
- Add option for named key ids to GraphML writing. (#3960)
- fix documentation (#3958)
- Correct handling of zero-weight edges in all_shortest_paths (#3783)
- Fix documentation typo (#3965)
- Fix: documentation of simrank_similarity_numpy (#3954)
- Fix for #3930 (source & target columns not overwritten when converting to pd.DataFrame) (#3935)
- Add weight function for shortest simple paths for #3948 (#3949)
- Fix defination of communicability (#3973)
- Fix simrank_similarity with directed graph input (#3961)
- Fixed weakening of voting ability (#3970)
- implemented faster sweep algorithm for kernighan_lin_bisection (#3858)
- Fix issue #3926 (#3928)
- Update CONTRIBUTORS.rst (#3982)
- Deprecate context_manager reversed in favor of reversed_view (#3983)
- Update CONTRIBUTORS.rst (#3987)
- Enhancement for voterank (#3972)
- add d-separation algorithm (#3974)
- DOC: added see also section to find_cycle (#3999)
- improve docs for subgraph_view filter_egde (#4010)
- Fix exception causes in dag.py (#4000)
- use raise from for exceptions in to_networkx_graph (#4009)
- Fix exception causes and messages in 12 modules (#4012)
- Fix typo: `np.int` -> `np.int_` (#4013)
- fix a typo (#4017)
- change documentation (#3981)
- algorithms for regular graphs (#3925)
- Typo Hand should be Hans (#4025)
- DOC: Add testing bullet to CONTRIBUTING. (#4035)
- Update Sphinx
- Update optional/test deps
- Add governance/values/nexp/roadmap
- Improve formatting of None in tutorial (#3986)
- Fixes DiGraph spelling in docstring (#3892)
- Update links to Py3 docs (#4042)
- Add method to clear edges only (#3477)
- Fix exception causes and messages all over the codebase (#4015)
- Handle kwds explicitly in draw_networkx (#4033)
- return empty generator instead of empty list (#3967)
- Correctly infer numpy float types (#3919)
- MAINT: Update from_graph6_bytes arg/docs. (#4034)
- Add URLs/banner/titlebar to documentation (#4044)
- Add negative cycle detection heuristic (#3879)
- Remove unused imports (#3855)
- Fixed Bug in generate_gml(G, stringizer=None) (#3841)
- Raise NetworkXError when k < 2 (#3761)
- MAINT: rm np.matrix from alg. conn. module
- MAINT: rm np.matrix from attribute_ac.
- MAINT,TST: Parametrize methods in TestAlgebraicConnectivity.
- MAINT,TST: parametrize buckminsterfullerene test.
- MAINT,TST: Remove unused _methods class attr
- MAINT,TST: Parametrize TestSpectralOrdering.
- excluded self/recursive edges  (#4037)
- WIP: Change EdgeDataView __contains__ feature (2nd attempt) (#3845)
- Index edges for multi graph simple paths (#3358)
- ENH: Add new graph_hashing feature
- Fix pandas deprecation
- Organize removal of deprecated code
- Update sphinx
- ENH: Add roots and timeout to GED (#4026)
- Make gallery more prominent
- Add an implementation for interval_graph and its unit tests (#3705)
- Fixed typo in kamada_kawai_layout docstring (#4059)
- Remove completeness condition from minimum weight full matching (#4057)
- Implemented multipartite_layout (#3815)
- added new Link Prediction algorithm (CCPA) (#4028)
- add the option of sorting node's neighbors during bfs traversal  (#4029)
- TST: remove int64 specification from test. (#4055)
- Ran pyupgrade --py36plus
- Remove trailing spaces
- Tell psf/black to ignore specific np.arrays
- Format w/ black
- Add pre-commit hook to for psf/black
- Merge pull request #4060 from jarrodmillman/black
- Fix a few typos in matching docstrings (#4063)
- fix bug for to_scipy_sparse_matrix function (#3985)
- Update documentation of minimum weight full matching (#4062)
- Add maximum weight clique algorithm (#4016)
- Clear pygraphviz object after creating networkx object (#4070)
- Use newer osx on travis (#4075)
- Install Python after updating brew (#4079)
- Add link to black (#4078)
- Improves docs regarding aliases of erdos-reyni graph generators (#4074)
- MAINT: Remove dependency version info from INSTALL (#4081)
- Simplify top-level directory (#4087)
- DOC: Fix return types in laplacianmatrix. (#4090)
- add modularity to the docs (#4096)
- Allow G.remove_edges_from(nx.selfloops_edges(G)) (#4080)
- MAINT: rm private fn in favor of numpy builtin. (#4094)
- Allow custom keys for multiedges in from_pandas_edgelist (#4076)
- Fix planar_layout docstring (#4097)
- DOC: Rewording re: numpy.matrix
- MAINT: rm to/from_numpy_matrix internally
- Merge pull request #4093 from rossbar/rm_npmatrix
- Remove copyright boilerplate (#4105)
- Update contributor guide (#4088)
- Add function to calculate path cost for a specified path (#4069)
- Update docstring for from_pandas_edgelist (#4108)
- Add max_weight_clique to doc (#4110)
- Update deprecation policyt (#4112)
- Improve modularity calculation (#4103)
- Add team gallery (#4117)
- CI: Setup circle CI for documentation builds (#4119)
- Build pdf (#4123)
- DOC: Suggestions and improvments from tutorial readthrough (#4121)
- Enable 3.9-dev on travis (#4124)
- Fix parse_edgelist behavior with multiple attributes (#4125)
- CI: temporary fix for CI latex installation issues (#4131)
- Updated draw_networkx to accept numpy array for edgelist (#4132)
- Add tree isomorphism (#4067)
- MAINT: Switch to abc-based isinstance checks in to_networkx_graph (#4136)
- Use dict instead of OrderedDict since dict is ordered by default from Python 3.6. (#4145)
- MAINT: fixups to parse_edgelist. (#4128)
- Update apt-get on circleci image (#4147)
- add rescale_layout_dict to change scale of the layout_dicts (#4154)
- Update dependencies
- Remove gdal from requirements
- relabel_nodes now preserves edges in multigraphs (#4066)
- MAINT,TST: Improve coverage of nx_agraph module (#4156)
- Get steiner_tree to work with MultiGraphs by postprocessing (#4160)
- junction_tree for #1012 (#4004)
- API: Add `show` kwarg to view_pygraphviz. (#4155)
- Prepare for turning chordal_graph_cliques into a generator (#4162)
- Docs update (#4161)
- Remove unnecessary nx imports from doctests (#4163)
- MultiGraph from graphml with explicit edge ids #3470 (#3763)
- Update sphinx dep (#4164)
- Add edge label in GEXF writer as an optional attribute (#3347)
- First Draft of Release Notes for v2.5 (#4159)
- Designate 2.5rc1 release
- Bump release version
- Update deprecations in release notes (#4166)
- DOC: Update docstrings for public functions in threshold module (#4167)
- Format python in docstrings (#4168)
- DOC,BLD: Fix doc build warning from markup error. (#4174)

It contained the following 3 merges:

- fixed a typo (#3759)
- Use psf/black (#4060)
- MAINT: Replace internal usage of to_numpy_matrix and from_numpy_matrix (#4093)


Contributors
------------

- Adnan Abdulmuttaleb
- Abhi
- Antoine-H
- Salim BELHADDAD
- Ross Barnowski
- Lukas Bernwald
- Isaac Boates
- Kelly Boothby
- Matthias Bruhns
- Mahmut Bulut
- Rüdiger Busche
- Gaetano Carpinato
- Nikos Chan
- Harold Chan
- Camden Cheek
- Daniel
- Daniel-Davies
- Bastian David
- Christoph Deil
- Tanguy Fardet
- 赵丰 (Zhao Feng)
- Andy Garfield
- Oded Green
- Drew H
- Alex Henrie
- Kang Hong Jin
- Manas Joshi
- Søren Fuglede Jørgensen
- Aabir Abubaker Kar
- Folgert Karsdorp
- Suny Kim
- Don Kirkby
- Katherine Klise
- Steve Kowalik
- Ilia Kurenkov
- Whi Kwon
- Paolo Lammens
- Zachary Lawrence
- Sanghack Lee
- Anton Lodder
- Lukas Lösche
- Eric Ma
- Mackyboy12
- Christoph Martin
- Alex Marvin
- Mattwmaster58
- James McDermott
- Jarrod Millman
- Ibraheem Moosa
- Yohsuke Murase
- Neil
- Harri Nieminen
- Danny Niquette
- Carlos G. Oliver
- Juan Orduz
- Austin Orr
- Pedro Ortale
- Aditya Pal
- PalAditya
- Jose Pinilla
- PranayAnchuri
- Jorge Martín Pérez
- Pradeep Reddy Raamana
- Ram Rachum
- David Radcliffe
- Federico Rosato
- Tom Russell
- Craig Schmidt
- Jonathan Schneider
- Dan Schult
- Mridul Seth
- Karthikeyan Singaravelan
- Songyu-Wang
- Kanishk Tantia
- Jeremias Traub
- James Trimble
- Shashi Tripathi
- Stefan van der Walt
- Jonatan Westholm
- Kazimierz Wojciechowski
- Jangwon Yie
- adnanmuttaleb
- anentropic
- arunwise
- beckedorf
- ernstklrb
- farhanbhoraniya
- fj128
- gseva
- haochenucr
- johnthagen
- kiryph
- muratgu
- ryan-duve
- sauxpa
- tombeek111
- willpeppo
