NetworkX 1.8
============

Release date:  28 July 2013

Highlights
~~~~~~~~~~
- Faster (linear-time) graphicality tests and Havel-Hakimi graph generators
- Directed Laplacian matrix generator
- Katz centrality algorithm
- Functions to generate all simple paths
- Improved shapefile reader
- More flexible weighted projection of bipartite graphs
- Faster topological sort, descendants and ancestors of DAGs
- Scaling parameter for force-directed layout

Bug fixes
~~~~~~~~~
- Error with average weighted connectivity for digraphs, correct normalized laplacian with self-loops, load betweenness for single node graphs, isolated nodes missing from dfs/bfs trees, normalize HITS using l1, handle density of graphs with self loops

- Cleaner handling of current figure status with Matplotlib, Pajek files now don't write troublesome header line, default alpha value for GEXF files, read curved edges from yEd GraphML


For full details of the issues closed for this release (added features and bug fixes) see: https://github.com/networkx/networkx/issues?milestone=1&page=1&state=closed

API changes
~~~~~~~~~~~

* Laplacian functions now all return matrices.  To get a numpy array from a matrix use L = nx.laplacian_matrix(G).A

* is_directed_acyclic_graph() now returns false on undirected graphs (instead of raising exception)

* cycles returned from simple_cycles() do not include repeated last node


