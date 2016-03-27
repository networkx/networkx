*********************************
Version 1.8 notes and API changes
*********************************

This page reflects API changes from networkx-1.7 to networkx-1.8.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .

* Laplacian functions now all return matrices.  To get a numpy array from a matrix use L = nx.laplacian_matrix(G).A

* is_directed_acyclic_graph() now returns false on undirected graphs (instead of raising exception)

* cycles returned from simple_cycles() do not include repeated last node


