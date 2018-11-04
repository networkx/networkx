Announcement: NetworkX 2.0
==========================

We're happy to announce the release of NetworkX 2.0!
NetworkX is a Python package for the creation, manipulation, and study of the
structure, dynamics, and functions of complex networks.

For more information, please visit our `website <http://networkx.github.io/>`_
and our `gallery of examples
<https://networkx.github.io/documentation/latest/auto_examples/index.html>`_.
Please send comments and questions to the `networkx-discuss mailing list
<http://groups.google.com/group/networkx-discuss>`_.

Highlights
----------

This release is the result of over two years of work with 1212 commits and
193 merges by 86 contributors. Highlights include:

- We have made major changes to the methods in the Multi/Di/Graph classes.
  There is a `migration guide for people moving from 1.X to 2.0
  <https://networkx.github.io/documentation/latest/release/migration_guide_from_1.x_to_2.0.html>`_.

- We updated the documentation system.

API Changes
-----------

* Base Graph Class Changes
  With the release of NetworkX 2.0 we are moving towards a view/iterator reporting API.
  We used to have two methods for the same property of the graph, one that returns a
  list and one that returns an iterator. With 2.0 we have replaced them with a view.
  A view is a read-only object that is quick to create, automatically updated, and
  provides basic access like iteration, membership and set operations where appropriate.
  For example, ``G.nodes()`` used to return a list and ``G.nodes_iter()`` an iterator.
  Now ``G.nodes()`` returns a view and ``G.nodes_iter()`` is removed. ``G.degree()``
  returns a view with ``(node, degree)`` iteration, so that ``dict(G.degree())``
  returns a dict keyed by node with degree as value.
  The old behavior

    >>> G = nx.complete_graph(5)
    >>> G.nodes()  # doctest: +SKIP
    [0, 1, 2, 3, 4]
    >>> G.nodes_iter()  # doctest: +SKIP
    <dictionary-keyiterator at ...>

  has changed to

    >>> G = nx.complete_graph(5)
    >>> G.nodes()
    NodeView((0, 1, 2, 3, 4))
    >>> list(G.nodes())
    [0, 1, 2, 3, 4]

  New feature include lookup of node and edge data from the views, property
  access without parentheses, and set operations.

    >>> G.add_node(3, color='blue')
    >>> G.nodes[3]
    {'color': 'blue'}
    >>> G.nodes & {3, 4, 5}
    set([3, 4])

  The following methods have changed:

    * Graph/MultiGraph

      * ``G.nodes()``
      * ``G.edges()``
      * ``G.neighbors()``
      * ``G.adjacency_list()`` and ``G.adjacency_iter()`` to ``G.adjacency()``
      * ``G.degree()``
      * ``G.subgraph()``
      * ``G.copy()``
      * ``G.__class__()`` should be replaced with ``G.fresh_copy()``

    * DiGraph/MultiDiGraph

      * ``G.nodes()``
      * ``G.edges()``
      * ``G.in_edges()``
      * ``G.out_edges()``
      * ``G.degree()``
      * ``G.in_degree()``
      * ``G.out_degree()``
      * ``G.reverse()``

  The following deprecated methods will be removed in a future release (3.0?).
      * ``G.node``, ``G.edge`` (replaced by G.nodes, G.edges)
      * ``G.add_path``, ``G.add_cycle``, ``G.add_star`` (Now ``nx.add_path(G,...``)
      * ``G.selfloop_edges``, ``G.nodes_with_selfloops``, ``G.number_of_selfloops``
        (Now ``nx.selfloop_edges(G)``, etc)

  Many subclasses have been changed accordingly such as:
    * AntiGraph
    * OrderedGraph and friends
    * Examples such as ThinGraph that inherit from Graph

* [`#2107 <https://github.com/networkx/networkx/pull/2107>`_]
  The Graph class methods ``add_edge`` and ``add_edges_from`` no longer
  allow the use of the ``attr_dict`` parameter.  Instead use keyword arguments.
  Thus ``G.add_edge(1, 2, {'color': 'red'})`` becomes
  ``G.add_edge(1, 2, color='red')``.
  Note that this only works if the attribute name is a string. For non-string
  attributes you will need to add the edge and then update manually using
  e.g. ``G.edges[1, 2].update({0: "zero"})``

* [`#1577 <https://github.com/networkx/networkx/pull/1577>`_]
  In addition to minimum spanning trees, a new function for calculating maximum
  spanning trees is now provided. The new API consists of four functions:
  ``minimum_spanning_edges``, ``maximum_spanning_edges``,
  ``minimum_spanning_tree``, and ``maximum_spanning_tree``.
  All of these functions accept an ``algorithm`` parameter which specifies the
  algorithm to use when finding the minimum or maximum spanning tree. Currently,
  Kruskal's and Prim's algorithms are implemented, defined as 'kruskal' and
  'prim', respectively. If nothing is specified, Kruskal's algorithm is used.
  For example, to calculate the maximum spanning tree of a graph using Kruskal's
  algorithm, the function ``maximum_spanning_tree`` has to be called like::

      >>> nx.maximum_spanning_tree(G, algorithm='kruskal')

  The ``algorithm`` parameter is new and appears before the existing ``weight``
  parameter. So existing code that did not explicitly name the optional
  ``weight`` parameter will need to be updated::

      >>> nx.minimum_spanning_tree(G, 'mass')  # old
      >>> nx.minimum_spanning_tree(G, weight='mass') # new

  In the above, we are still relying on the the functions being imported into the
  top-level  namespace. We do not have immediate plans to deprecate this approach,
  but we recommend the following instead::

       >>> from networkx.algorithms import tree
       # recommended
       >>> tree.minimum_spanning_tree(G, algorithm='kruskal', weight='mass')
       >>> tree.minimum_spanning_edges(G, algorithm='prim', weight='mass')

* [`#1445 <https://github.com/networkx/networkx/pull/1445>`_]
  Most of the ``shortest_path`` algorithms now raise a ``NodeNotFound`` exception
  when a source or a target are not present in the graph.

* [`#2326 <https://github.com/networkx/networkx/pull/2326>`_]
  Centrality algorithms were harmonized with respect to the default behavior of
  the weight parameter. The default value of the ``weight`` keyword argument has
  been changed from ``weight`` to ``None``.  This affects the
  following centrality functions:

  - :func:`approximate_current_flow_betweenness_centrality()`
  - :func:`current_flow_betweenness_centrality()`
  - :func:`current_flow_betweenness_centrality_subset()`
  - :func:`current_flow_closeness_centrality()`
  - :func:`edge_current_flow_betweenness_centrality()`
  - :func:`edge_current_flow_betweenness_centrality_subset()`
  - :func:`eigenvector_centrality()`
  - :func:`eigenvector_centrality_numpy()`
  - :func:`katz_centrality()`
  - :func:`katz_centrality_numpy()`

* [`#2420 <https://github.com/networkx/networkx/pull/2420>`_]
  New community detection algorithm provided. Fluid Communities is an
  asynchronous algorithm based on the simple idea of fluids interacting in an
  environment, expanding and pushing each other. The algorithm is completely
  described in `"Fluid Communities: A Competitive and Highly Scalable Community
  Detection Algorithm" <https://arxiv.org/pdf/1703.09307.pdf>`_.

* [`#2510 <https://github.com/networkx/networkx/pull/2510>`_ and
  `#2508 <https://github.com/networkx/networkx/pull/2508>`_]
  ``single_source_dijkstra``, ``multi_source_dijkstra`` and functions that use
  these now have new behavior when ``target`` is specified. Instead of
  returning dicts for distances and paths a 2-tuple of ``(distance, path)`` is
  returned.  When ``target`` is not specified the return value is still 2
  dicts.

* [`#2553 <https://github.com/networkx/networkx/pull/2553>`_]
  ``set_node_attributes()`` and ``set_edge_attributes()`` now accept
  dict-of-dict input of shape ``{node/edge: {name: value}}`` in addition to
  previous valid inputs: ``{node/edge: value}`` and ``value``. The order of the
  parameters changed also: The second parameter "values" is the value argument
  and the third parameter "name" is the name of the attribute. "name" has
  default value ``None`` in which case "values" must be the newly allowed form
  containing names. Previously "name" came second without default, and "values"
  came third.

* [`#2604 <https://github.com/networkx/networkx/pull/2604>`_] Move selfloop
  methods out of base classes to networkx functions.
  ``G.number_of_selfloops()``, ``G.selfloop_edges()``,
  ``G.nodes_with_selfloops()`` are now ``nx.number_of_selfloops(G)``,
  ``nx.selfloop_edges(G)``, ``nx.nodes_with_selfloops(G)``.

  ``G.node`` and ``G.edge`` are removed. Their functionality are replaced by
  ``G.nodes`` and ``G.edges``.

* [`#2558 <https://github.com/networkx/networkx/pull/2558>`_]
  Previously, the function ``from_pandas_dataframe`` assumed that the dataframe
  has edge-list like structures, but ``to_pandas_dataframe`` generates an
  adjacency matrix.  We now provide four functions ``from_pandas_edgelist``,
  ``to_pandas_edgelist``, ``from_pandas_adjacency``, and ``to_pandas_adjacency``.

* [`#2620 <https://github.com/networkx/networkx/pull/2620>`_]
  Removed ``draw_nx``, please use ``draw`` or ``draw_networkx``.

* [`#1662 <https://github.com/networkx/networkx/pull/1662>`_]
  Rewrote ``topolgical_sort`` as a generator.  It no longer accepts
  ``reverse`` or ``nbunch`` arguments and is slightly faster.
  Added ``lexicographical_topological_sort``, which accepts a key.

Deprecations
------------

The following deprecated functions will be removed in 2.1.

- The function ``bellman_ford`` has been deprecated in favor of
  ``bellman_ford_predecessor_and_distance``.

- The functions ``to_pandas_dataframe`` and ``from_pandas_dataframe`` have been
  deprecated in favor of ``to_pandas_adjacency``, ``from_pandas_adjacency``,
  ``to_pandas_edgelist``, and ``from_pandas_edgelist``.

Contributors to this release
----------------------------

- Niels van Adrichem
- Kevin Arvai
- Ali Baharev
- Moritz Emanuel Beber
- Livio Bioglio
- Jake Bogerd
- Moreno Bonaventura
- Raphaël Bournhonesque
- Matthew Brett
- James Clough
- Marco Cognetta
- Jamie Cox
- Jon Crall
- Robert Davidson
- Nikhil Desai
- DonQuixoteDeLaMancha
- Dosenpfand
- Allen Downey
- Enrico
- Jens Erat
- Jeffrey Finkelstein
- Minas Gjoka
- Aravind Gollakota
- Thomas Grainger
- Aric Hagberg
- Harry
- Yawara ISHIDA
- Bilal AL JAMMAL
- Ryan James
- Omer Katz
- Janis Klaise
- Valentin Lorentz
- Alessandro Luongo
- Francois Malassenet
- Arya McCarthy
- Michael-E-Rose
- Peleg Michaeli
- Jarrod Millman
- Chris Morin
- Sanggyu Nam
- Nishant Nikhil
- Rhile Nova
- Ramil Nugmanov
- Juan Nunez-Iglesias
- Pim Otte
- Ferran Parés
- Richard Penney
- Phobia
- Tristan Poupard
- Sebastian Pucilowski
- Alexander Rodriguez
- Michael E. Rose
- Alex Ryan
- Zachary Sailer
- René Saitenmacher
- Felipe Schneider
- Dan Schult
- Scinawa
- Michael Seifert
- Mohammad Hossein Sekhavat
- Mridul Seth
- SkyTodInfi
- Stacey Smolash
- Jordi Torrents
- Martin Törnwall
- Jannis Vamvas
- Luca Verginer
- Prayag Verma
- Peter Wills
- Ianto Lin Xi
- Heqing Ya
- aryamccarthy
- chebee7i
- definitelyuncertain
- jfinkels
- juliensiebert
- leotrs
- leycec
- mcognetta
- numpde
- root
- salotz
- scott-vsi
- thegreathippo
- vpodpecan
- yash14123
- Neil Girdhar

Pull requests merged in this release
------------------------------------

- Gml read fix. (#1962)
- Small changes leftover from #1847 (#1966)
- Fix k_core for directed graphs. Add tests (#1963)
- Communicability fix (#1958)
- Allows weight functions in shortest path functions (#1690)
- minor doc changes on weighted.py (#1969)
- Fix minimum_st_edge_cut documentation. (#1977)
- Fix all_node_cuts corner cases: cycle and complete graphs. (#1976)
- Change add_path/star/cycle from methods to functions (#1970)
- branch 'edge-subgraph' from @jfinkels (#1740)
- Corrected eppstein matching (#1955)
- Nose ignore docstrings (#1980)
- Edited Doc Makefile so clean doesn't delete the examples folder (#1967)
- bug fix in convert_matrix.py (#1983)
- Avoid unnecessary eigenval sort in pagerank_numpy (#1986)
- Fix a typo in install.rst (#1991)
- Adds unorderable nodes test for dag_longest_path. (#1999)
- Improve drawing test scripts (typos, newlines, methods) (#1992)
- Improves test coverage for A* shortest path. (#1988)
- Improves test coverage for avg degree connectivity (#1987)
- Fix Graph() docstring to reflect input flexibility (#2006)
-  Fix sphinx autosummary doc generation errors. (#2026)
- Improve gexf.py (#2010)
- Readme.rst should mention Decorator package is required. (#2009)
- fix_duplicate_kwarg: Fix a duplicate kwarg that was causing to_agraph… (#2005)
- Cleans documentation for graph6 and sparse6 I/O. (#2002)
- Remove http server example (#2001)
- Generalize and improve docstrings of node_link.py (#2000)
- fix issue #1948 and PEP8 formatting (#2031)
- Uses weight function for dijkstra_path_length. (#2033)
- Change default role for sphinx to 'obj' (#2027)
- fixed typo s/abritrary/arbitrary/ (#2035)
- Fix bug in dtype-valued matrices (#2038)
- Adds example for using Graph.nodes() with default (#2040)
- Clarifies some examples for relabel_nodes(). (#2041)
- Cleans code and documentation for graph power. (#2042)
- Cleans the classes.function module. (#2043)
- UnboundLocalError if called with an empty graph (#2047)
- Standardized Bellman-Ford function calls (#1910)
- Nobody is in IRC (#2059)
- Uses add_weighted_edges_from function in MST test. (#2061)
- Adds multi-source Dijkstra's algorithm (#2073)
- Adds Voronoi cells algorithm (#2074)
- Fixes several issues with the Girvan-Newman partitioning function. Fixes #1703, #1725, #1799  (#1972)
- Moves is_path from utils to simple_paths. (#1921)
- add max_iter and tol parameter for numpy version (#2013)
- Remove draw_graphviz function. Fixes #1997 (#2077)
- Fixes #1998 edge_load function needs documentation. (#2075)
- Update fixcoverage.py (#2080)
- Support digraphs in approximate min vertex cover (#2039)
- Simplifies code in functions for greedy coloring. (#1680)
- Allows arbitrary metric in geometric generators. (#1679)
- Fix spring_layout for single node graph. (#2081)
- Updates set_{node,edge}_attributes and docs. (#1935)
- Fixes tests for maximal matching. (#1919)
- Adds LFM benchmark graph generator for communities (#1727)
- Adds global and local efficiency functions. (#1521)
- Apply alphas to individual nodes (#1289)
- Code and tests for temporal VF2 (#1653)
- extend convert_bool in gexf.py and graphml.py to all valid boolean  (#1063)
- Remove encoded ... to plain ascii (#2086)
- Use not_implemented_for() for in_degree_centrality() and out_degree_centrality() (#2084)
- Issue 2072 weighted modularity (#2088)
- Simplifies eigenvector centrality implementation. (#1708)
- Fjmalass nodes as tuples (#2089)
- Generator rename (#2090)
- Ensure links in doc ```See also``` sections (#2082)
- Document integer-only numeric mixing (#2085)
- doc sphinx error removal (#2091)
- Correct see also links (#2095)
- Adjust layout.py function signatures, docs, exposure (#2096)
- Adds missing __all__ attributes. (#2098)
- Fixes 2 bugs in dominance frontier code (#2092)
- Created two new files: joint_degree_seq.py and test_joint_degree_seq.… (#2011)
- Adds Borůvka's minimum spanning tree algorithm. (#1873)
- Adds global/local reaching centrality functions. (#2099)
- Remove conflicts from #1894 (Update Exception Classes) (#2100)
- Add Exceptions for missing source in shortest_path (#2102)
- Docs for compose now warn about MultiGraph edgekeys (#2101)
- Improve Notes section on simplex and friends docs. (#2104)
- Add Dinitz' algorithm for maximum flow problems. (#1978)
- Removed duplicated method/doc (add_edges_from) (#1)
- Bugfix for generic_multiedge_match (Issue #2114) (#2124)
- Fix for 2015. (#2)
- add_node, add_edge attr_dict change. (#2132)
- Handle graph name attribute in relabel_nodes (#2136)
- Fix fruchterman reingold bug and add more tests to layouts. (#2141)
- Adds exception: failed power iteration convergence (#2143)
- Tweak iteration logic of HITS (#2142)
- Fix PageRank personalize docstring (#2148)
- Set default source=None for dfs_tree (#2149)
- Fix docs for maximal_matching and tensor_product (#2158)
- Isolate edge key generation in multigraphs (#2150)
- Sort centralities together and outsource dispersion (#2083)
- Changed classic generators to use generators instead of lists (#2167)
- Adds beam search traversal algorithm with example (#2129)
- Turan graph (#2172)
- Removes irrelevant Notes section from docstring (#2178)
- Corrects logarithm base in example (#2179)
- Minor correction in documentation (#2180)
- Add Boykov Kolmogorov algorithm for maximum flow problems. (#2122)
- Remove temporary files after tests are run. (#2202)
- Add support for subgraphs with no edges in convert_matrix.to_scipy_sparse_matrix. (#2199)
- Add support for reading adjacency matrix in readwrite.pajek.parse_pajek. (#2200)
- Moves Graph Atlas to data file. (#2064)
- Refactor Dinitz' algorithm implementation. (#2196)
- Use arrays instead of matrices in scipy.linalg.expm() (#2208)
- Making in_edges equivalent to out_edges (#2206)
- Fix tests failing because of ordering issues. (#2207)
- Fix code escaping. (#2214)
- Add adjlist_outer_dict_factory. (#2222)
- Typo in scale free network generator documentation (#2225)
- Add link to nx.drawing.layout instead of mentionning nx.layout. (#2224)
- Example not working in tutorial (#2230)
- don't assume nodes are sortable when running dag_longest_path (#2228)
- Correct typo (#2236)
- Use ego graph when computing local efficiency (#2246)
- Make harmonic centrality more memory-efficient (#2247)
- have dag_longest_path_length return path length, not edge count (#2237)
- Added transitive_reduction in dag (#2215)
- alpha kwarg not used in pylab label drawing, added it here.   (#2269)
- Make PyDot Support Great Again (#2272)
- Unnecessary array copying in katz_centrality_numpy ? (#2287)
- Switch to faster smallest-last algorithm implementation. (#2268)
- Adds example for getting all simple edge paths. Fixes #718  (#2260)
- Remove obsolete testing tools. (#2303)
- Correct error in minimum_spanning_arborescence (#2285)
- Yield string, not dict, in dfs_labeled_edges. (#2277)
- Removes unnecessary convert_to_(un)directed func (#2259)
- Complete multipartite graph docs (#2221)
- fix LPA bug, see issues/2219 (#2227)
- Generalized degree (#2220)
- Turan docs (#2218)
- Fix broken link to the description of the P2G format. (#2211)
- Test ordering (#2209)
- add example of node weights (#2250)
- added paramether nbunch (#2253)
- Adds unit tests for using dtype with to_numpy_matrix (#2257)
- Adds chain decomposition algorithm. (#2284)
- add the Hoffman-Singleton graph (#2275)
- Allow grid_graph generator to accept tuple dim argument (#2320)
- psuedo -> pseudo (fixing typo) (#2322)
- Corrects navigable small world graph param docs (#2321)
- Fix bug in find_cycle. (#2324)
- flip source target (#2309)
- Simpler version of digitsrep(..) function (#2330)
- change articulation_points so that it only returns every vertex once (#2333)
- Use faster random geometric graph implementation. (#2337)
- Allow community asyn_lpa test to have two answers (#2339)
- Fix broken links and remove pdf files from Makefile (#2344)
- Documents orderable node requirement for isom. (#2302)
- Adds modularity measure for communities. (#1729)
- Simplifies degree sequence graph generators. (#1866)
- Adds tree encoding and decoding functions. (#1874)
- Corrects number_of_edges docs for directed graphs (#2360)
- Adds multigraph keys to Eulerian circuits (#2359)
- Update predecessors/successors in edge subgraph (#2373)
- Fix for #2364 (#2372)
- Raise an Exception for disconnected Graphs in bipartite.sets (#2375)
- fixes typo in NetworkXNotImplemented (#2385)
- Check alternating paths using iterative DFS in to_vertex_cover. (#2386)
- Fix typos in generating NXError in networkx.linalg.graphmatrix.incidence_matrix (#2395)
- [Fixes #2342] remove calls to plt.hold(), deprecated in mpl2.0 (#2397)
- Fix broken links (#2414)
- Fix all tests for 3.6 (#2413)
- Improve bipartite documentation. (#2402)
- correct logic in GEXFWriter (#2399)
- list optional dependencies in setup.py (#2398)
- Gitwash update (#2371)
- Added cytoscape JSON handling (#2351)
- Fix for issues #2328 and #2332 (#2366)
- Workaround for gdal python3.6 at travis and more doctests fixes (#2416)
- Fixed bug on custom attrs usage: unavailable iteritems method for dict. (#2461)
- Fix sphinx errors and class outlines (#2480)
- Note the precondition that graphs are directed and acyclic (#2500)
- Add CONTRIBUTE file (#2501)
- Remove external module (#2521)
- Ensure `make html` doesn't fail build on exit (#2530)
- Cherry pick missing commits (#2535)
- Document release process (#2539)
- Update copyright (#2551)
- Remove deprecated code (#2536)
- Improve docs (#2555)
- WIP: Add note on how to estimate appropriate values for alpha (#2583)
- Travis refactor (#2596)
- Create separate functions for df as edge-lists and adjacency matrices (#2558)
- Use texext for math_dollar (#2609)
- Add drawing tests (#2617)
- Add threshold tests (#2622)
- Update docs (#2623)
- Prep beta release (#2624)
- Refactor travis tests and deploy docs with travis (#2647)
- matplotlib 2.1 deprecated is_string_like (#2659)
- topolgical_sort, lexicographical_topological_sort (#1662)
