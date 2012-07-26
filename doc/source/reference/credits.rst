Credits
-------

NetworkX was originally written by Aric Hagberg, Dan Schult, and Pieter Swart,
and has been developed with the help of many others.   

Thanks to Guido van Rossum for the idea of using Python for
implementing a graph data structure
http://www.python.org/doc/essays/graphs.html

Thanks to David Eppstein for the idea of representing a graph G so
that "for n in G" loops over the nodes in G and G[n] are node n's
neighbors.

Thanks to everyone who has improved NetworkX by contributing code,
bug reports (and fixes), documentation, and input on design, featues,
and the future of NetworkX.

Thanks especially to the following contributors:

 - Katy Bold contributed the Karate Club graph.
 - Hernan Rozenfeld added dorogovtsev_goltsev_mendes_graph and did 
   stress testing.
 - Brendt Wohlberg added examples from the Stanford GraphBase.
 - Jim Bagrow reported bugs in the search methods. 
 - Holly Johnsen helped fix the path based centrality measures. 
 - Arnar Flatberg fixed the graph laplacian routines.
 - Chris Myers suggested using None as a default datatype, suggested
   improvements for the IO routines, added grid generator index tuple
   labeling and associated routines, and reported bugs.
 - Joel Miller tested and improved the connected components methods
   fixed bugs and typos in the graph generators, and contributed
   the random clustered graph generator.
 - Keith Briggs sorted out naming issues for random graphs and
   wrote dense_gnm_random_graph.
 - Ignacio Rozada provided the Krapivsky-Redner graph generator.
 - Phillipp Pagel helped fix eccentricity etc. for disconnected graphs. 
 - Sverre Sundsdal contributed bidirectional shortest path and
   Dijkstra routines, s-metric computation and graph generation  
 - Ross M. Richardson contributed the expected degree graph generator
   and helped test the pygraphviz interface.
 - Christopher Ellison implemented the VF2 isomorphism algorithm
   and is a core developer.
 - Eben Kenah contributed the strongly connected components and
   DFS functions.
 - Sasha Gutfriend contributed edge betweenness algorithms.
 - Udi Weinsberg helped develop intersection and difference operators.
 - Matteo Dell'Amico wrote the random regular graph generator.
 - Andrew Conway contributed ego_graph, eigenvector centrality,
   line graph and much more.
 - Raf Guns wrote the GraphML writer.
 - Salim Fadhley and Matteo Dell'Amico contributed the A* algorithm.
 - Fabrice Desclaux contributed the Matplotlib edge labeling code.
 - Arpad Horvath fixed the barabasi_albert_graph() generator.
 - Minh Van Nguyen contributed the connected_watts_strogatz_graph()
   and documentation for the Graph and MultiGraph classes.
 - Willem Ligtenberg contributed the directed scale free graph
   generator.
 - Loïc Séguin-C. contributed the Ford-Fulkerson max flow and min cut 
   algorithms, and ported all of NetworkX to Python3.  He is a 
   NetworkX core developer.
 - Paul McGuire improved the performance of the GML data parser.
 - Jesus Cerquides contributed the chordal graph algorithms.
 - Ben Edwards contributed tree generating functions, the rich club 
   coefficient algorithm, the graph product functions, and a whole lot
   of other useful nuts and bolts.
 - Jon Olav Vik contributed cycle finding algorithms.
 - Hugh Brown improved the words.py example from the n^2 algorithm.
 - Ben Reilly contributed the shapefile reader and writer.
 - Leo Lopes contributed the maximal independent set algorithm.
 - Jordi Torrents contributed the bipartite clustering, bipartite
   node redundancy, square clustering, other bipartite 
   and articulation point algorithms.
 - Dheeraj M R contributed the distance-regular testing algorithm
 - Franck Kalala contributed the subgraph_centrality and communicability 
   algorithms
 - Simon Knight improved the GraphML functions to handle yEd/yfiles data,
   and to handle types correctly.
 - Conrad Lee contributed the k-clique community finding algorithm.
 - Sérgio Nery Simões wrote the function for finding all simple paths,
   and all shortest paths.
 - Robert King contributed union, disjoint union, compose, and intersection
   operators that work on lists of graphs.
 - Nick Mancuso wrote the approximation algorithms for dominating set,
   edge dominating set, independent set, max clique, and min-weighted
   vertex cover.
