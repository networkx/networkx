NetworkX 1.5
============

Release date:  4 June 2011

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
   specified edge attribute (default='weight')
   (ticket https://networkx.lanl.gov/trac/ticket/509)

 - Test for :mod:`distance regular <networkx.algorithms.distance_regular>` graphs
 - Fast :mod:`directed Erdős-Renyi graph  <networkx.generators.random_graphs>` generator
 - Fast :mod:`expected degree graph  <networkx.generators.degree_seq>` generator
 - :mod:`Navigable small world  <networkx.generators.geometric>` generator
 - :mod:`Waxman model <networkx.generators.geometric>` generator
 - :mod:`Geographical threshold graph <networkx.generators.geometric>` generator
 - :mod:`Karate Club, Florentine Families, and Davis' Women's Club <networkx.generators.social>` graphs

Weighted graph algorithms
-------------------------

Many 'weighted' graph algorithms now take optional parameter to
specify which edge attribute should be used for the weight
(default='weight') (ticket https://networkx.lanl.gov/trac/ticket/509)

In some cases the parameter name was changed from weighted_edges,
or weighted, to weight.  Here is how to specify which edge attribute
will be used in the algorithms:

- Use weight=None to consider all weights equally (unweighted case)

- Use weight=True or weight='weight' to use the 'weight' edge attribute

- Use weight='other' to use the 'other' edge attribute

Algorithms affected are:

betweenness_centrality, closeness_centrality, edge_bewteeness_centrality,
betweeness_centrality_subset, edge_betweenness_centrality_subset,
betweenness_centrality_source, load, closness_vitality,
weiner_index, spectral_bipartivity
current_flow_betweenness_centrality,
edge_current_flow_betweenness_centrality,
current_flow_betweenness_centrality_subset,
edge_current_flow_betweenness_centrality_subset,
laplacian, normalized_laplacian, adj_matrix, adjacency_spectrum,
shortest_path, shortest_path_length, average_shortest_path_length,
single_source_dijkstra_path_basic, astar_path, astar_path_length

Random geometric graph
----------------------

The random geometric graph generator has been simplified.
It no longer supports the create_using, repel, or verbose parameters.
An optional pos keyword was added to allow specification of node positions.

Bug fixes
~~~~~~~~~
 - Fix edge handling for multigraphs in networkx/graphviz interface
   (ticket https://networkx.lanl.gov/trac/ticket/507)
 - Update networkx/pydot interface for new versions of pydot
   (ticket https://networkx.lanl.gov/trac/ticket/506)
   (ticket https://networkx.lanl.gov/trac/ticket/535)
 - Fix negative cycle handling in Bellman-Ford
   (ticket https://networkx.lanl.gov/trac/ticket/502)
 - Write more attributes with GraphML and GML formats
   (ticket https://networkx.lanl.gov/trac/ticket/480)
 - Handle white space better in read_edgelist
   (ticket https://networkx.lanl.gov/trac/ticket/513)
 - Better parsing of Pajek format files
   (ticket https://networkx.lanl.gov/trac/ticket/524)
   (ticket https://networkx.lanl.gov/trac/ticket/542)
 - Isolates functions work with directed graphs
   (ticket https://networkx.lanl.gov/trac/ticket/526)
 - Faster conversion to numpy matrices
   (ticket https://networkx.lanl.gov/trac/ticket/529)
 - Add graph['name'] and use properties to access Graph.name
   (ticket https://networkx.lanl.gov/trac/ticket/544)
 - Topological sort confused None and 0
   (ticket https://networkx.lanl.gov/trac/ticket/546)
 - GEXF writer mishandled weight=0
   (ticket https://networkx.lanl.gov/trac/ticket/550)
 - Speedup in SciPy version of PageRank
   (ticket https://networkx.lanl.gov/trac/ticket/554)
 - Numpy PageRank node order incorrect + speedups
   (ticket https://networkx.lanl.gov/trac/ticket/555)
