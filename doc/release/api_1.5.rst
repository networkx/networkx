*********************************
Version 1.5 notes and API changes
*********************************

This page reflects API changes from networkx-1.4 to networkx-1.5.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .

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

