NetworkX 1.6
============

Release date:  20 November 2011

Highlights
~~~~~~~~~~

New functions for finding articulation points, generating random bipartite graphs, constructing adjacency matrix representations, forming graph products, computing assortativity coefficients, measuring subgraph centrality and communicability, finding k-clique communities, and writing JSON format output.

New examples for drawing with D3 JavaScript library, and ordering matrices with the Cuthill-McKee algorithm.

More memory efficient implementation of current-flow betweenness and new approximation algorithms for current-flow betweenness and shortest-path betweenness.

Simplified handling of "weight" attributes for algorithms that use weights/costs/values.

Updated all code to work with the PyPy Python implementation http://pypy.org which produces faster performance on many algorithms.

Graph Classes
-------------

The degree* methods in the graph classes (Graph, DiGraph, MultiGraph,
MultiDiGraph) now take an optional weight= keyword that allows computing
weighted degree with arbitrary (numerical) edge attributes.  Setting
weight=None is equivalent to the previous weighted=False.


Weighted graph algorithms
-------------------------

Many 'weighted' graph algorithms now take optional parameter to
specify which edge attribute should be used for the weight
(default='weight') (ticket https://networkx.lanl.gov/trac/ticket/573)

In some cases the parameter name was changed from weighted, to weight.  Here is
how to specify which edge attribute will be used in the algorithms:

- Use weight=None to consider all weights equally (unweighted case)

- Use weight='weight' to use the 'weight' edge attribute

- Use weight='other' to use the 'other' edge attribute

Algorithms affected are:

to_scipy_sparse_matrix,
clustering,
average_clustering,
bipartite.degree,
spectral_layout,
neighbor_degree,
is_isomorphic,
betweenness_centrality,
betweenness_centrality_subset,
vitality,
load_centrality,
mincost,
shortest_path,
shortest_path_length,
average_shortest_path_length


Isomorphisms
------------

Node and edge attributes are now more easily incorporated into isomorphism
checks via the 'node_match' and 'edge_match' parameters.  As part of this
change, the following classes were removed::

    WeightedGraphMatcher
    WeightedDiGraphMatcher
    WeightedMultiGraphMatcher
    WeightedMultiDiGraphMatcher

The function signature for 'is_isomorphic' is now simply::

    is_isomorphic(g1, g2, node_match=None, edge_match=None)

See its docstring for more details.  To aid in the creation of 'node_match'
and 'edge_match' functions, users are encouraged to work with::

    categorical_node_match
    categorical_edge_match
    categorical_multiedge_match
    numerical_node_match
    numerical_edge_match
    numerical_multiedge_match
    generic_node_match
    generic_edge_match
    generic_multiedge_match

These functions construct functions which can be passed to 'is_isomorphic'.
Finally, note that the above functions are not imported into the top-level
namespace and should be accessed from 'networkx.algorithms.isomorphism'.
A useful import statement that will be repeated throughout documentation is::

    import networkx.algorithms.isomorphism as iso

Other
-----
* attracting_components

  A list of lists is returned instead of a list of tuples.

* condensation

  The condensation algorithm now takes a second argument (scc) and returns a
  graph with nodes labeled as integers instead of node tuples.

* degree connectivity

  average_in_degree_connectivity and average_out_degree_connectivity have
  been replaced with

  average_degree_connectivity(G, source='in', target='in')

  and

  average_degree_connectivity(G, source='out', target='out')

* neighbor degree

  average_neighbor_in_degree and  average_neighbor_out_degreey have
  have been replaced with

  average_neighbor_degree(G, source='in', target='in')

  and

  average_neighbor_degree(G, source='out', target='out')

