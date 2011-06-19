*********************************
Version 1.6 notes and API changes
*********************************

This page reflects API changes from networkx-1.5 to networkx-1.6.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .

Graph Classes
-------------

The degree* methods in the graph classes (Graph, DiGraph, MultiGraph,
MultiDiGraph) now take an optional weight= keyword that allows computing
weighted degree with arbitrary (numerical) edge attributes.  Setting weight=None is equivalent to the previous weighted=False.


Weighted graph algorithms
-------------------------

Many 'weighted' graph algorithms now take optional parameter to 
specifiy which edge attribute should be used for the weight
(default='weight') (:ticket:`573`)

In some cases the parameter name was changed from weighted, to weight.  Here is how to specify which edge attribute will be used in the algorithms:

- Use weight=None to consider all weights equally (unweighted case)

- Use weight='weight' to use the 'weight' edge atribute

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


