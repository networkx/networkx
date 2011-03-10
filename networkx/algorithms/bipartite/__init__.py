"""
This module provides functions and operations for bipartite graphs.
Bipartite graphs G(X,Y,E) have two node sets X,Y and edges in E that only connect nodes from opposite sets.

NetworkX does not have a custom bipartite graph class but the Graph() or 
DiGraph() classes can be used to represent bipartite graphs.

For example:`

>>> import networkx as nx
>>> top_nodes=[1,1,2,3,3]
>>> bottom_nodes=['a','b','b','b','c']
>>> edges=zip(top_nodes,bottom_nodes) # create 2-tuples of edges
>>> B=nx.Graph(edges) 
>>> print(B.edges())
[('a', 1), (1, 'b'), (2, 'b'), ('b', 3), ('c', 3)]

Some of the functions such as bipartite_density and projected_graph take 
a node set as an argument in addition to the graph B.

>>> print(nx.bipartite_density(B,top_nodes))
1.0
>>> G=nx.projected_graph(B,bottom_nodes)
>>> G.edges()
[('a', 'b'), ('c', 'b')]

You can find the bipartite node sets using

>>> X,Y=nx.bipartite_sets(B)
>>> print(list(X))
['a', 'c', 'b']
>>> print(list(Y))
[1, 2, 3]

"""
from networkx.algorithms.bipartite.basic import *
from networkx.algorithms.bipartite.clustering import *
from networkx.algorithms.bipartite.projection import *
from networkx.algorithms.bipartite.redundancy import *
from networkx.algorithms.bipartite.spectral import *



