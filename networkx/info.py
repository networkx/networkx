"""
Graph
Graph


Graph
-----

An undirected graph that allows self-loops, but not multiple (parallel)
edges.  Nodes are arbitrary hashable objects.
Arbitrary data may be associated with each edge.  Edge data that cannot 
be treated as a numeric weight will not work with some algorithms in 
NetworkX.  If you use such edge data, set Graph.weighted=False to avoid 
confusion.

An empty graph is created with

>>> G=nx.Graph()
   
DiGraph
-------

A directed graph that allows self-loops, but not multiple 
(parallel) edges.   Edge and node data is the same as for Graph.
Subclass of Graph.

An empty digraph is created with

>>> G=nx.DiGraph()


MultiGraph
----------
An undirected graph that allows multiple (parallel) edges with arbitrary 
data on the edges.
Subclass of Graph.

An empty multigraph is created with

>>> G=nx.MultiGraph()


MultiDiGraph
------------
A directed graph that allows multiple (parallel) edges with arbitrary 
data on the edges.
Subclass of DiGraph which is a subclass of Graph.

An empty multidigraph is created with

>>> G=nx.MultiDiGraph()

LabeledGraph
------------

An undirected graph that stores node labels/dict in the dict G.labels.
This has no impact on other computations, but allows you to associate
any value object with each node.
Subclass of Graph.

An empty labeledgraph is created with

>>> G=nx.LabeledGraph()

LabeledDiGraph
--------------

A directed version of LabeledGraph.
Subclass of LabeledGraph and DiGraph which are each subclasses of Graph.

An empty labeleddigraph is created with

>>> G=nx.LabeledDiGraph()


Notation
========

The following shorthand is used throughout NetworkX documentation and code:
(we use mathematical notation n,v,w,... to indicate a node, v=vertex=node).
 
G,G1,G2,H,etc:
   Graphs

n,n1,n2,u,v,v1,v2:
   nodes (vertices)

nlist:
   a list of nodes (vertices)

nbunch:
   a "bunch" of nodes (vertices).
   An nbunch is either a single node of the graph or
   any iterable container/iterator of nodes.  The distinction
   is determined by checking if nbunch is in the graph.
   If you use iterable containers as nodes you should be 
   careful when using nbunch.

e=(n1,n2):
   an edge (a python "2-tuple"), also written n1-n2 (if undirected)
   and n1->n2 (if directed). 
   
e=(n1,n2,x):
   an edge triple ("3-tuple") containing the two nodes connected and the 
   edge data/label/object stored associated with the edge. The object x,
   or a list of objects (if multiedges=True), can be obtained using
   G.get_edge(n1,n2)

elist:
   a list of edges (as 2- or 3-tuples)

ebunch:
   a bunch of edges (as 2- or 3-tuples).
   An ebunch is any iterable (non-string) container
   of edge-tuples (either 2-tuples, 3-tuples or a mixture).

Warning:
  - The ordering of objects within an arbitrary nbunch/ebunch can be
    machine-dependent.
  - Algorithms should treat an arbitrary nbunch/ebunch as
    once-through-and-exhausted iterable containers.
  - len(nbunch) and len(ebunch) need not be defined.
    

Attributes
==========

Each graph class provides three attributes to help identify what
algorithms may work with that graph type.  Each attribute is a
boolean value (True/False).

    - G.weighted
    - G.directed
    - G.multigraph


G.weighted is the only one that should be changed directly by users.
It specifies whether the edge data can be treated as a numeric weight.
Algorithms that require numeric edge weights will give unpredictable 
results if, e.g. strings are associated with edges.  If you use 
non-numeric edge data, you should set G.weighted to False.

Changing G.directed and G.multigraph should be accomplished by converting
the graph to a new graph type with e.g. DiGraph(G) or MultiGraph(G).


Methods
=======

Each class provides basic graph methods.

Mutating Graph methods
----------------------
   
    - G.add_node(n), G.add_nodes_from(nlist)
    - G.remove_node(n), G.remove_nodes_from(nlist)
    - G.add_edge(n1,n2), G.add_edges_from(ebunch)
    - G.remove_edge(n1,n2), G.remove_edges_from(ebunch)
    - G.clear()
    - G.subgraph(nbunch,copy=False)

    - G.add_path(nlist)
    - G.add_cycle(nlist)
    - G.add_star(nlist)

Non-mutating Graph methods
--------------------------

    - len(G)
    - G.has_node(n)
    - n in G (equivalent to G.has_node(n))
    - for n in G: (iterate through the nodes of G)
    - G.nodes()
    - G.nodes_iter()
    - G.number_of_nodes(), G.order()
    - G.neighbors(n)
    - G.neighbors_iter(n) # iterator over neighbors
    - G[n]  (returns a dict of edge data keyed by neighbor nodes of n)
    - G.number_of_edges(), G.size()
    - G.get_edge(n1,n2,default=0)  (returns edge data or default)
    - G.has_edge(n1,n2), G.has_neighbor(n1,n2), G.get_edge(n1,n2)
    - G.edges(), G.edges(n), G.edges(nbunch)      
    - G.edges_iter(), G.edges_iter(n), G.edges_iter(nbunch)
    - G.adjacency_list()   (returns a list of neighbor lists)
    - G.adjacency_iter()   (iterates through (n,G[n]) pairs)
    - G.degree(n), G.degree(nbunch), G.degree()
    - G.degree(n, weighted=True)
    - G.degree_iter()
    - G.directed()
    - G.nodes_with_selfloops(), G.selfloop_edges()
    - G.number_of_selfloops()
    - G.info()  # print variaous info about a graph
    - G.nbunch_iter(nbunch)  # iterator of nodes in G and nbunch

Methods returning a new graph
-----------------------------

    - G.subgraph(nbunch)
    - G.copy()
    - G.to_undirected
    - G.to_directed
    
Directed Graphs
---------------

    - DG.successors_iter(n), DG.predecessors_iter(n) 
    - DG.successors(n), DG.predecessors(n) 
    - DG.has_successor(n), DG.has_predecessor(n) 
    Note: neighbors() return only successors.
    - DG.in_degree(), DG.out_degree() 
    Note: degree() refers to both in and out edges.
    - DG.reverse()


Implementation Notes
====================

The graph classes implement graphs using data structures
based on a dictionary of dictionaries implementation of adjacency lists.
The outer dictionary is keyed by nodes to an adjacency dictionary.
The adjacency dictionary is keyed by neighbor with value being the 
edge data associated with the edge between node and neighbor.
The default edge data is the numeric value 1.
The dictionary of dictionary structure  allows fast addition,
removal and lookup of nodes and neighbors in large graphs.  

Multigraphs
-----------

Multigraphs use a dictionary of dictionaries of lists data
structure.  Upon adding the first edge connecting two nodes,
a list is created to store the edge data for all edges between
these two nodes.  As implemented, a Multigraph is actually a 
Graph with edge data being a list.  But, we prefer to think of 
it as a Multigraph as a graph that allows multiple edges between
the same two nodes.

"""
