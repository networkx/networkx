Credits
-------

NetworkX was originally written by Aric Hagberg, Dan Schult, and Pieter Swart
with the help of many others.   

Thanks to Guido van Rossum for the idea of using Python for
implementing a graph data structure  
http://www.python.org/doc/essays/graphs.html

Thanks to David Eppstein for the idea of representing a graph G
so that "for n in G" loops over the nodes in G and G[n] are node n's 
neighbors.      

Thanks to all those who have improved NetworkX by contributing code,
bug reports (and fixes), documentation, and input on design, featues,
and the future of NetworkX.

Thanks especially to the following contributors.

 - Katy Bold contributed the Karate Club graph 

 - Hernan Rozenfeld added dorogovtsev_goltsev_mendes_graph and did 
   stress testing

 - Brendt Wohlberg added examples from the Stanford GraphBase

 - Jim Bagrow reported bugs in the search methods 

 - Holly Johnsen helped fix the path based centrality measures 

 - Arnar Flatberg fixed the graph laplacian routines

 - Chris Myers suggested using None as a default datatype, suggested
   improvements for the IO routines, added grid generator index tuple
   labeling and associated routines, and reported bugs

 - Joel Miller tested and improved the connected components methods
   fixed bugs and typos in the graph generators, and contributed
   the random clustered graph generator.

 - Keith Briggs sorted out naming issues for random graphs and
   wrote dense_gnm_random_graph

 - Ignacio Rozada provided the Krapivsky-Redner graph generator

 - Phillipp Pagel helped fix eccentricity etc. for disconnected graphs 

 - Sverre Sundsdal contributed bidirectional shortest path and
   Dijkstra routines, s-metric computation and graph generation  

 - Ross M. Richardson contributed the expected degree graph generator
   and helped test the pygraphviz interface

 - Christopher Ellison implemented the VF2 isomorphism algorithm
   and contributed the code for matching all the graph types.

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



