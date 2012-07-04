..  -*- coding: utf-8 -*-
.. currentmodule:: networkx

Release Log
===========

Networkx-1.7
------------
Release date:  4 July 2012

Highlights
~~~~~~~~~~

- New functions for k-clique community finding, flow hierarchy,
  union, disjoint union, compose, and intersection operators that work on 
  lists of graphs, and creating the biadjacency matrix of a bipartite graph.

- New approximation algorithms for dominating set, edge dominating set,
  independent set, max clique, and min-weighted vertex cover.

- Many bug fixes and other improvements.

For full details of the tickets closed for this release (added features and bug fixes) see:
https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.7

API Changes
~~~~~~~~~~~
See :doc:`api_1.7`


Networkx-1.6
------------

Release date:  20 November 2011

Highlights
~~~~~~~~~~

New functions for finding articulation points, generating random bipartite graphs, constructing adjacency matrix representations, forming graph products, computing assortativity coefficients, measuring subgraph centrality and communicability, finding k-clique communities, and writing JSON format output.

New examples for drawing with D3 Javascript library, and ordering matrices with the Cuthill-McKee algorithm.

More memory efficient implementation of current-flow betweenness and new approximation algorithms for current-flow betweenness and shortest-path betweenness.

Simplified handling of "weight" attributes for algorithms that use weights/costs/values.  See :doc:`api_1.6`.

Updated all code to work with the PyPy Python implementation http://pypy.org which produces faster performance on many algorithms.

For full details of the tickets closed for this release (added features and bug fixes) see:
https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.6

API Changes
~~~~~~~~~~~
See :doc:`api_1.6`


Networkx-1.5
------------

Release date:  4 June 2011

For full details of the tickets closed for this release see:
https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.5

Highlights
~~~~~~~~~~

New features
~~~~~~~~~~~~
 - Algorithms for :mod:`generating <networkx.generators.bipartite>` 
   and :mod:`analyzing <networkx.algorithms.bipartite>` bipartite graphs
 - :mod:`Maximal independent set <networkx.algorithms.mis>` algorithm
 - :mod:`Erdős-Gallai graphical degree sequence test <networkx.generators.degree_seq>`
 - :mod:`Negative edge cycle test <networkx.algorithms.shortest_paths.weighted>`
 - More memory efficient :mod:`Dijkstra path length <networkx.algorithms.shortest_paths.weighted>` with cutoff parameter
 - :mod:`Weighted clustering coefficient <networkx.algorithms.cluster>`
 - Read and write version 1.2 of :mod:`GEXF reader <networkx.readwrite.gexf>` format
 - :mod:`Neighbor degree correlation <networkx.algorithms.neighbor_degree>` 
   that handle subsets of nodes
 - :mod:`In-place node relabeling <networkx.relabel>` 
 - Many 'weighted' graph algorithms now take optional parameter to use 
   specified edge attribute (default='weight') (:ticket:`509`)

 - Test for :mod:`distance regular <networkx.algorithms.distance_regular>` graphs
 - Fast :mod:`directed Erdős-Renyi graph  <networkx.generators.random_graphs>` generator
 - Fast :mod:`expected degree graph  <networkx.generators.degree_seq>` generator
 - :mod:`Navigable small world  <networkx.generators.geometric>` generator
 - :mod:`Waxman model <networkx.generators.geometric>` generator
 - :mod:`Geographical threshold graph <networkx.generators.geometric>` generator
 - :mod:`Karate Club, Florentine Families, and Davis' Women's Club <networkx.generators.social>` graphs


API Changes
~~~~~~~~~~~
See :doc:`api_1.5`


Bug fixes
~~~~~~~~~
 - Fix edge handling for multigraphs in networkx/graphviz interface 
   (:ticket:`507`)
 - Update networkx/pydot interface for new versions of pydot 
   (:ticket:`506`), (:ticket:`535`)
 - Fix negative cycle handling in Bellman-Ford (:ticket:`502`)
 - Write more attributes with GraphML and GML formats (:ticket:`480`)
 - Handle white space better in read_edgelist (:ticket:`513`)
 - Better parsing of Pajek format files (:ticket:`524`) (:ticket:`542`)
 - Isolates functions work with directed graphs (:ticket:`526`)
 - Faster conversion to numpy matrices (:ticket:`529`)
 - Add graph['name'] and use properties to access Graph.name (:ticket:`544`)
 - Topological sort confused None and 0 (:ticket:`546`)
 - GEXF writer mishandled weight=0 (:ticket:`550`)
 - Speedup in SciPy version of PageRank (:ticket:`554`)
 - Numpy PageRank node order incorrect + speedups (:ticket:`555`)

Networkx-1.4
------------

Release date:  23 January 2011

New features
~~~~~~~~~~~~
 - :mod:`k-shell,k-crust,k-corona <networkx.algorithms.core>`
 - :mod:`read GraphML files from yEd <networkx.readwrite.graphml>`
 - :mod:`read/write GEXF format files <networkx.readwrite.gexf>`
 - :mod:`find cycles in a directed graph <networkx.algorithms.cycles>`
 - :mod:`DFS <networkx.algorithms.traversal.depth_first_search>` and :mod:`BFS <networkx.algorithms.traversal.breadth_first_search>` algorithms
 - :mod:`chordal graph functions <networkx.algorithms.chordal.chordal_alg>`
 - :mod:`Prim's algorithm for minimum spanning tree <networkx.algorithms.mst>`
 - :mod:`r-ary tree generator <networkx.generators.classic>`
 - :mod:`rich club coefficient <networkx.algorithms.richclub>`
 - NumPy matrix version of :mod:`Floyd's algorithm for all-pairs shortest path  <networkx.algorithms.shortest_paths.dense>`
 - :mod:`read GIS shapefiles <networkx.readwrite.nx_shp>`
 - :mod:`functions to get and set node and edge attributes <networkx.classes.function>`
 - and more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.4

API Changes
~~~~~~~~~~~
 - :mod:`gnp_random_graph() <networkx.generators.random_graphs>` now takes a 
   directed=True|False keyword instead of create_using 
 - :mod:`gnm_random_graph() <networkx.generators.random_graphs>` now takes a 
   directed=True|False keyword instead of create_using 

Bug fixes
~~~~~~~~~
  - see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.4



Networkx-1.3
------------

Release date:  28 August 2010

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
 - Works with Python versions 2.6, 2.7, 3.1, and 3.2 (but not 2.4 and 2.5).
 - :mod:`Minimum cost flow algorithms <networkx.algorithms.flow>`
 - :mod:`Bellman-Ford shortest paths <networkx.algorithms.shortest_paths.weighted>`
 - :mod:`GraphML reader and writer <networkx.readwrite.graphml>` 
 - :mod:`More exception/error types <networkx.exception>` 
 - Updated many tests to unittest style.  Run with: "import networkx; networkx.test()" (requires nose testing package)
 - and more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.3

API Changes
~~~~~~~~~~~
 - :mod:`minimum_spanning_tree() now returns a NetworkX Graph (a tree or forest) <networkx.algorithms.mst>` 

Bug fixes
~~~~~~~~~
  - see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.3


Networkx-1.2
------------

Release date:  28 July 2010

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
 - :mod:`Ford-Fulkerson max flow and min cut <networkx.algorithms.flow>` 
 - :mod:`Closeness vitality <networkx.algorithms.vitality>` 
 - :mod:`Eulerian circuits <networkx.algorithms.euler>` 
 - :mod:`Functions for isolates <networkx.algorithms.isolates>` 
 - :mod:`Simpler s_max generator <networkx.generators.degree_seq>` 
 - Compatible with IronPython-2.6
 - Improved testing functionality: import networkx; networkx.test() tests
   entire package and skips tests with missing optional packages
 - All tests work with Python-2.4
 - and more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.2


Networkx-1.1
------------

Release date:  21 April 2010

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
 - :mod:`Algorithm for finding a basis for graph cycles <networkx.algorithms.cycles>` 
 - :mod:`Blockmodeling <networkx.algorithms.block>` 
 - :mod:`Assortativity and mixing matrices <networkx.algorithms.mixing>` 
 - :mod:`in-degree and out-degree centrality <networkx.algorithms.centrality.degree>` 
 - :mod:`Attracting components <networkx.algorithms.components.attracting>` 
   and  :mod:`condensation <networkx.algorithms.components.strongly_connected>`.
 - :mod:`Weakly connected components <networkx.algorithms.components.weakly_connected>`
 - :mod:`Simpler interface to shortest path algorithms <networkx.algorithms.shortest_paths.generic>` 
 - :mod:`Edgelist format to read and write data with attributes <networkx.readwrite.edgelist>` 
 - :mod:`Attribute matrices <networkx.linalg.spectrum>` 
 - :mod:`GML reader for nested attributes <networkx.readwrite.gml>` 
 - Current-flow (random walk) 
   :mod:`betweenness <networkx.algorithms.centrality.current_flow_betweenness>` 
   and 
   :mod:`closeness <networkx.algorithms.centrality.current_flow_closeness>`. 
 - :mod:`Directed configuration model <networkx.generators.degree_seq>`,
   and  :mod:`directed random graph model <networkx.generators.random_graphs>`.
 - Improved documentation of drawing, shortest paths, and other algorithms
 - Many more tests, can be run with "import networkx; networkx.test()"
 - and much more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.1

API Changes
~~~~~~~~~~~
Returning dictionaries
**********************
Several of the algorithms and the degree() method now return dictionaries
keyed by node instead of lists.  In some cases there was a with_labels
keyword which is no longer necessary.  For example,
 
>>> G=nx.Graph()
>>> G.add_edge('a','b')
>>> G.degree() # returns dictionary of degree keyed by node
{'a': 1, 'b': 1}
 
Asking for the degree of a single node still returns a single number
 
>>> G.degree('a')
1

The following now return dictionaries by default (instead of lists)
and the with_labels keyword has been removed:
 
 - :meth:`Graph.degree`, 
   :meth:`MultiGraph.degree`,
   :meth:`DiGraph.degree`, 
   :meth:`DiGraph.in_degree`, 
   :meth:`DiGraph.out_degree`,
   :meth:`MultiDiGraph.degree`, 
   :meth:`MultiDiGraph.in_degree`, 
   :meth:`MultiDiGraph.out_degree`.
 - :func:`clustering`, 
   :func:`triangles`
 - :func:`node_clique_number`, 
   :func:`number_of_cliques`, 
   :func:`cliques_containing_node`
 - :func:`eccentricity`
   

The following now return dictionaries by default (instead of lists)

 - :func:`pagerank`
 - :func:`hits`


Adding nodes
************
add_nodes_from now accepts (node,attrdict) two-tuples

>>> G=nx.Graph()
>>> G.add_nodes_from([(1,{'color':'red'})])

Examples
~~~~~~~~
 - `Mayvi2 drawing <http://networkx.lanl.gov/examples/drawing/mayavi2_spring.html>`_
 - `Blockmodel <http://networkx.lanl.gov/examples/algorithms/blockmodel.html>`_
 - `Sampson's monastery <http://networkx.lanl.gov/examples/drawing/sampson.html>`_
 - `Ego graph <http://networkx.lanl.gov/examples/drawing/ego_graph.html>`_

Bug fixes
~~~~~~~~~
 - Support graph attributes with union, intersection, and other graph operations
 - Improve subgraph speed (and related algorithms such as 
   connected_components_subgraphs())
 - Handle multigraphs in more operators (e.g. union)   
 - Handle double-quoted labels with pydot
 - Normalize betweenness_centrality for undirected graphs correctly 
 - Normalize eigenvector_centrality by l2 norm
 - :func:`read_gml` now returns multigraphs

Networkx-1.0.1
--------------

Release date:  11 Jan 2010

See: https://networkx.lanl.gov/trac/timeline

Bug fix release for missing setup.py in manifest.


Networkx-1.0
------------

Release date:  8 Jan 2010

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
This release has significant changes to parts of the graph API
to allow graph, node, and edge attributes.
See http://networkx.lanl.gov//reference/api_changes.html

 - Update Graph, DiGraph, and MultiGraph classes to allow attributes.
 - Default edge data is now an empty dictionary (was the integer 1)   
 - Difference and intersection operators
 - Average shortest path
 - A* (A-Star) algorithm
 - PageRank, HITS, and eigenvector centrality
 - Read Pajek files
 - Line graphs
 - Minimum spanning tree (Kruskal's algorithm)
 - Dense and sparse Fruchterman-Reingold layout
 - Random clustered graph generator
 - Directed scale-free graph generator
 - Faster random regular graph generator
 - Improved edge color and label drawing with Matplotlib
 - and much more, see  https://networkx.lanl.gov/trac/query?status=closed&group=milestone&milestone=networkx-1.0

Examples
~~~~~~~~
 - Update to work with networkx-1.0 API
 - Graph subclass example


Networkx-0.99
-------------

Release date:  18 November 2008

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
This release has significant changes to parts of the graph API.
See http://networkx.lanl.gov//reference/api_changes.html

 - Update Graph and DiGraph classes to use weighted graphs as default
   Change in API for performance and code simplicity.
 - New MultiGraph and MultiDiGraph classes (replace XGraph and XDiGraph)
 - Update to use Sphinx documentation system http://networkx.lanl.gov/
 - Developer site at https://networkx.lanl.gov/trac/
 - Experimental LabeledGraph and LabeledDiGraph
 - Moved package and file layout to subdirectories.

Bug fixes
~~~~~~~~~
 - handle root= option to draw_graphviz correctly 

Examples
~~~~~~~~
 - Update to work with networkx-0.99 API
 - Drawing examples now use matplotlib.pyplot interface
 - Improved drawings in many examples
 - New examples - see http://networkx.lanl.gov/examples/


NetworkX-0.37
---------------

Release date: 17 August 2008

See: https://networkx.lanl.gov/trac/timeline

NetworkX now requires Python 2.4 or later for full functionality.

New features
~~~~~~~~~~~~
 - Edge coloring and node line widths with Matplotlib drawings
 - Update pydot functions to work with pydot-1.0.2
 - Maximum-weight matching algorithm
 - Ubigraph interface for 3D OpenGL layout and drawing
 - Pajek graph file format reader and writer
 - p2g graph file format reader and writer
 - Secondary sort in topological sort

Bug fixes
~~~~~~~~~
 - Better edge data handling with GML writer 
 - Edge betweenness fix for XGraph with default data of None
 - Handle Matplotlib version strings (allow "pre")
 - Interface to PyGraphviz (to_agraph()) now handles parallel edges
 - Fix bug in copy from XGraph to XGraph with multiedges
 - Use SciPy sparse lil matrix format instead of coo format 
 - Clear up ambiguous cases for Barabasi-Albert model
 - Better care of color maps with Matplotlib when drawing colored nodes
   and edges 
 - Fix error handling in layout.py

Examples
~~~~~~~~
 - Ubigraph examples showing 3D drawing 


NetworkX-0.36
---------------

Release date: 13 January 2008

See: https://networkx.lanl.gov/trac/timeline


New features
~~~~~~~~~~~~
  - GML format graph reader, tests, and example (football.py)	
  - edge_betweenness() and load_betweenness()

Bug fixes
~~~~~~~~~
  - remove obsolete parts of pygraphviz interface 
  - improve handling of Matplotlib version strings
  - write_dot() now writes parallel edges and self loops
  - is_bipartite() and bipartite_color() fixes 
  - configuration model speedup using random.shuffle()
  - convert with specified nodelist now works correctly
  - vf2 isomorphism checker updates

NetworkX-0.35.1
---------------

Release date: 27 July 2007

See: https://networkx.lanl.gov/trac/timeline

Small update to fix import readwrite problem and maintain Python2.3
compatibility.


NetworkX-0.35
-------------

Release date: 22 July 2007

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - algorithms for strongly connected components.
  - Brandes betweenness centrality algorithm (weighted and unweighted versions) 
  - closeness centrality for weighted graphs
  - dfs_preorder, dfs_postorder, dfs_tree, dfs_successor, dfs_predecessor
  - readers for GraphML, LEDA, sparse6, and graph6 formats.
  - allow arguments in graphviz_layout to be passed directly to graphviz

Bug fixes
~~~~~~~~~
  - more detailed installation instructions
  - replaced dfs_preorder,dfs_postorder (see search.py)
  - allow initial node positions in spectral_layout
  - report no error on attempting to draw empty graph
  - report errors correctly when using tuples as nodes #114
  - handle conversions from incomplete dict-of-dict data

NetworkX-0.34
-------------

Release date: 12 April 2007

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - benchmarks for graph classes	
  - Brandes betweenness centrality algorithm
  - Dijkstra predecessor and distance algorithm
  - xslt to convert DIA graphs to NetworkX
  - number_of_edges(u,v) counts edges between nodes u and v
  - run tests with python setup_egg.py test (needs setuptools)
    else use python -c "import networkx; networkx.test()"
  - is_isomorphic() that uses vf2 algorithm

Bug fixes
~~~~~~~~~
  - speedups of neighbors() 	
  - simplified Dijkstra's algorithm code
  - better exception handling for shortest paths   
  - get_edge(u,v) returns None (instead of exception) if no edge u-v
  - floyd_warshall_array fixes for negative weights
  - bad G467, docs, and unittest fixes for graph atlas
  - don't put nans in numpy or scipy sparse adjacency matrix
  - handle get_edge() exception (return None if no edge)
  - remove extra kwds arguments in many places
  - no multi counting edges in conversion to dict of lists for multigraphs
  - allow passing tuple to get_edge()
  - bad parameter order in node/edge betweenness 
  - edge betweenness doesn't fail with XGraph 
  - don't throw exceptions for nodes not in graph (silently ignore instead)
    in edges_* and degree_*

NetworkX-0.33
-------------

Release date: 27 November 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - draw edges with specified colormap
  - more efficient version of Floyd's algorithm for all pairs shortest path
  - use numpy only, Numeric is deprecated
  - include tests in source package (networkx/tests)
  - include documentation in source package (doc)
  - tests can now be run with
     >>> import networkx
     >>> networkx.test()    

Bug fixes
~~~~~~~~~
  - read_gpickle now works correctly with Windows
  - refactored large modules into smaller code files
  - degree(nbunch) now returns degrees in same order as nbunch 
  - degree() now works for multiedges=True
  - update node_boundary and edge_boundary for efficiency
  - edited documentation for graph classes, now mostly in info.py

Examples
~~~~~~~~
  - Draw edges with colormap



NetworkX-0.32
-------------

Release date: 29 September 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - Update to work with numpy-1.0x
  - Make egg usage optional: use python setup_egg.py bdist_egg to build egg
  - Generators and functions for bipartite graphs
  - Experimental classes for trees and forests
  - Support for new pygraphviz update (in nx_agraph.py) , see
    http://networkx.lanl.gov/pygraphviz/ for pygraphviz details 

Bug fixes
~~~~~~~~~
  - Handle special cases correctly in triangles function
  - Typos in documentation  
  - Handle special cases in shortest_path and shortest_path_length,
    allow cutoff parameter for maximum depth to search
  - Update examples: erdos_renyi.py, miles.py, roget,py, eigenvalues.py


Examples
~~~~~~~~
  - Expected degree sequence
  - New pygraphviz interface

NetworkX-0.31
-------------

Release date: 20 July 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
   - arbitrary node relabeling (use relabel_nodes)
   - conversion of NetworkX graphs to/from Python dict/list types,
     numpy matrix or array types, and scipy_sparse_matrix types
   - generator for random graphs with given expected degree sequence

Bug fixes
~~~~~~~~~
   - Allow drawing graphs with no edges using pylab
   - Use faster heapq in dijkstra 
   - Don't complain if X windows is not available

Examples
~~~~~~~~
   - update drawing examples


NetworkX-0.30
-------------


Release date: 23 June 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
   - update to work with Python 2.5 
   - bidirectional version of shortest_path and Dijkstra 
   - single_source_shortest_path and all_pairs_shortest_path
   - s-metric and experimental code to generate  maximal s-metric graph 
   - double_edge_swap and connected_double_edge_swap
   - Floyd's algorithm for all pairs shortest path
   - read and write unicode graph data to text files
   - read and write YAML format text files, http://yaml.org

Bug fixes
~~~~~~~~~
   - speed improvements (faster version of subgraph, is_connected)
   - added cumulative distribution and modified discrete distribution utilities
   - report error if DiGraphs are sent to connected_components routines
   - removed with_labels keywords for many functions where it was
     causing confusion
   - function name changes in shortest_path routines
   - saner internal handling of nbunch (node bunches), raise an
     exception if an nbunch isn't a node or iterable
   - better keyword handling in io.py allows reading multiple graphs 
   - don't mix Numeric and numpy arrays in graph layouts and drawing
   - avoid automatically rescaling matplotlib axes when redrawing graph layout

Examples
~~~~~~~~
   - unicode node labels 


NetworkX-0.29
-------------

Release date: 28 April 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
   - Algorithms for betweenness, eigenvalues, eigenvectors, and
     spectral projection for threshold graphs  
   - Use numpy when available
   - dense_gnm_random_graph generator
   - Generators for some directed graphs: GN, GNR, and GNC by Krapivsky
     and Redner 
   - Grid graph generators now label by index tuples.  Helper
     functions for manipulating labels.
   - relabel_nodes_with_function 


Bug fixes
~~~~~~~~~
   - Betweenness centrality now correctly uses Brandes definition and
     has normalization option outside main loop
   - Empty graph now labeled as empty_graph(n)
   - shortest_path_length used python2.4 generator feature
   - degree_sequence_tree off by one error caused nonconsecutive labeling
   - periodic_grid_2d_graph removed in favor of grid_2d_graph with
     periodic=True


NetworkX-0.28
-------------

Release date: 13 March 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - Option to construct Laplacian with rows and columns in specified order
  - Option in convert_node_labels_to_integers to use sorted order   
  - predecessor(G,n) function that returns dictionary of
    nodes with predecessors from breadth-first search of G 
    starting at node n.
    https://networkx.lanl.gov/trac/ticket/26

Examples
~~~~~~~~
  - Formation of giant component in binomial_graph:
  - Chess masters matches:
  - Gallery https://networkx.lanl.gov/gallery.html
  
Bug fixes
~~~~~~~~~
  - Adjusted names for random graphs.
     + erdos_renyi_graph=binomial_graph=gnp_graph: n nodes with 
       edge probability p
     + gnm_graph: n nodes and m edges
     + fast_gnp_random_graph: gnp for sparse graphs (small p)   
  - Documentation contains correct spelling of Barabási, Bollobás,
    Erdős, and Rényi in UTF-8 encoding
  - Increased speed of connected_components and related functions
    by using faster BFS algorithm in networkx.paths
    https://networkx.lanl.gov/trac/ticket/27     
  - XGraph and XDiGraph with multiedges=True produced error on delete_edge
  - Cleaned up docstring errors
  - Normalize names of some graphs to produce strings that represent
    calling sequence
  

NetworkX-0.27
-------------


Release date: 5 February 2006

See: https://networkx.lanl.gov/trac/timeline

New features
~~~~~~~~~~~~
  - sparse_binomial_graph: faster graph generator for sparse random graphs
  - read/write routines in io.py now handle XGraph() type and
    gzip and bzip2 files
  - optional mapping of type for read/write routine to allow
    on-the-fly conversion of node and edge datatype on read
  - Substantial changes related to digraphs and definitions of
    neighbors() and edges().  For digraphs edges=out_edges.
    Neighbors now returns a list of neighboring nodes with
    possible duplicates for graphs with parallel edges
    See https://networkx.lanl.gov/trac/ticket/24
  - Addition of out_edges, in_edges and corresponding out_neighbors
    and in_neighbors for digraphs.  For digraphs edges=out_edges.
   
Examples
~~~~~~~~
  - Minard's data for Napoleon's Russian campaign

Bug fixes
~~~~~~~~~
   - XGraph(multiedges=True) returns a copy of the list of edges
     for get_edge() 


NetworkX-0.26
-------------


Release date: 6 January 2006

New features
~~~~~~~~~~~~
  - Simpler interface to drawing with pylab
  - G.info(node=None) function returns short information about graph
    or node
  - adj_matrix now takes optional nodelist to force ordering of
    rows/columns in matrix
  - optional pygraphviz and pydot interface to graphviz is now callable as
    "graphviz" with pygraphviz preferred.  Use draw_graphviz(G).
   
Examples
~~~~~~~~
  - Several new examples showing how draw to graphs with various
    properties of nodes, edges, and labels

Bug fixes
~~~~~~~~~
   - Default data type for all graphs is now None (was the integer 1)
   - add_nodes_from now won't delete edges if nodes added already exist
   - Added missing names to generated graphs
   - Indexes for nodes in graphs start at zero by default (was 1)


NetworkX-0.25
-------------


Release date: 5 December 2005


New features
~~~~~~~~~~~~
  - Uses setuptools for installation http://peak.telecommunity.com/DevCenter/setuptools
  - Improved testing infrastructure, can now run python setup.py test
  - Added interface to draw graphs with pygraphviz
    https://networkx.lanl.gov/pygraphviz/
  - is_directed() function call

Examples
~~~~~~~~
  - Email example shows how to use XDiGraph with Python objects as
    edge data


Documentation
~~~~~~~~~~~~~
  - Reformat menu, minor changes to Readme, better stylesheet

Bug fixes
~~~~~~~~~
   - use create_using= instead of result= keywords for graph types
     in all cases
   - missing weights for degree 0 and 1 nodes in clustering     
   - configuration model now uses XGraph, returns graph with identical
     degree sequence as input sequence	   
   - fixed Dijkstra priority queue
   - fixed non-recursive toposort and is_directed_acyclic graph

NetworkX-0.24
-------------

Release date: 20 August 2005

Bug fixes
~~~~~~~~~
   - Update of Dijkstra algorithm code
   - dfs_successor now calls proper search method
   - Changed to list comprehension in DiGraph.reverse() for python2.3
     compatibility
   - Barabasi-Albert graph generator fixed
   - Attempt to add self loop should add node even if parallel edges not 
     allowed

NetworkX-0.23
-------------

Release date: 14 July 2005

The NetworkX web locations have changed:

http://networkx.lanl.gov/     - main documentation site
http://networkx.lanl.gov/svn/  - subversion source code repository
https://networkx.lanl.gov/trac/ - bug tracking and info


Important Change
~~~~~~~~~~~~~~~~
The naming conventions in NetworkX have changed.
The package name "NX" is now "networkx".

The suggested ways to import the NetworkX package are

 - import networkx
 - import networkx as NX
 - from networkx import *

New features
~~~~~~~~~~~~
  - DiGraph reverse
  - Graph generators
     + watts_strogatz_graph now does rewiring method
     + old watts_strogatz_graph->newman_watts_strogatz_graph

Examples
~~~~~~~~
Documentation
~~~~~~~~~~~~~
  - Changed to reflect NX-networkx change
  - main site is now https://networkx.lanl.gov/

Bug fixes
~~~~~~~~~
   - Fixed logic in io.py for reading DiGraphs.  
   - Path based centrality measures (betweenness, closeness)
     modified so they work on graphs that are not connected and
     produce the same result as if each connected component were
     considered separately.

NetworkX-0.22
-------------

Release date: 17 June 2005

New features
~~~~~~~~~~~~
  - Topological sort, testing for directed acyclic graphs (DAGs)
  - Dijkstra's algorithm for shortest paths in weighted graphs
  - Multidimensional layout with dim=n for drawing
  - 3d rendering demonstration with vtk
  - Graph generators
     + random_powerlaw_tree
     + dorogovtsev_goltsev_mendes_graph


Examples
~~~~~~~~
  - Kevin Bacon movie actor graph: Examples/kevin_bacon.py
  - Compute eigenvalues of graph Laplacian: Examples/eigenvalues.py
  - Atlas of small graphs: Examples/atlas.py
  
Documentation
~~~~~~~~~~~~~
  - Rewrite of setup scripts to install documentation and
    tests in documentation directory specified 



Bug fixes
~~~~~~~~~
   - Handle calls to edges() with non-node, non-iterable items.
   - truncated_tetrahedral_graph was just plain wrong
   - Speedup of betweenness_centrality code
   - bfs_path_length now returns correct lengths 
   - Catch error if target of search not in connected component of source
   - Code cleanup to label internal functions with _name
   - Changed import statement lines to always use "import NX" to
     protect name-spaces   
   - Other minor bug-fixes and testing added



