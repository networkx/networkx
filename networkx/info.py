"""
Graph classes
=============

Graph

   A simple graph that has no self-loops or multiple (parallel) edges.

   An empty graph is created with

   >>> G=Graph()
   
DiGraph

   A directed graph that has no self-loops or multiple (parallel) edges.
   Subclass of Graph.

   An empty digraph is created with

   >>> G=DiGraph()

XGraph

   A graph that has (optional) self-loops or multiple (parallel) edges
   and arbitrary data on the edges.
   Subclass of Graph.

   An empty graph is created with

   >>> G=XGraph()
   
XDiGraph

   A directed graph that has (optional) self-loops or multiple (parallel)
   edges and arbitrary data on the edges.

   A simple digraph that has no self-loops or multiple (parallel) edges.
   Subclass of DiGraph which is a subclass of Graph.

   An empty digraph is created with

   >>> G=DiGraph()


The XGraph and XDiGraph classes extend the Graph and DiGraph classes
by allowing (optional) self loops, multiedges and by decorating
each edge with an object x.  

Each XDiGraph or XGraph edge is a 3-tuple e=(n1,n2,x), 
representing an edge between nodes n1 and n2 that 
is decorated with the object x. Here n1 and n2 are (hashable) 
node objects and x is a (not necessarily hashable) edge object. 
If multiedges are allowed, G.get_edge(n1,n2) returns a 
list of edge objects.

Whether an XGraph or XDiGraph allow self-loops or multiple edges is
determined initially via parameters selfloops=True/False and 
multiedges=True/False. 
For example, the example empty XGraph created above is equivalent to

>>> G=XGraph(selfloops=False, multiedges=False)

Similar defaults hold for XDiGraph.  The command

>>> G=XDiGraph(multiedges=True)

creates an empty digraph G that does not allow selfloops 
but does allow for multiple (parallel) edges.  Methods exist 
for allowing or disallowing each feature after instatiation as well.

Note that if G is an XGraph then G.add_edge(n1,n2) will add 
the edge (n1,n2,None), and G.delete_edge(n1,n2) will attempt 
to delete the edge (n1,n2,None).
In the case of multiple edges between nodes n1 and n2, one can use
G.delete_multiedge(n1,n2) to delete all edges between n1 and n2.


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
    

Methods
=======

Each class provides basic graph methods.

Mutating Graph methods
----------------------
   
    - G.add_node(n), G.add_nodes_from(nbunch)
    - G.delete_node(n), G.delete_nodes_from(nbunch)
    - G.add_edge(n1,n2), G.add_edge(e), where e=(u,v)
    - G.add_edges_from(ebunch)
    - G.delete_edge(n1,n2), G.delete_edge(e), where e=(u,v)
    - G.delete_edges_from(ebunch)
    - G.add_path(nlist)
    - G.add_cycle(nlist)
    - G.clear()
    - G.subgraph(nbunch,inplace=True)

Non-mutating Graph methods
--------------------------

    - len(G)
    - G.has_node(n)
    - n in G (equivalent to G.has_node(n))
    - for n in G: (iterate through the nodes of G)
    - G.nodes()
    - G.nodes_iter()
    - G.has_edge(n1,n2), G.has_neighbor(n1,n2), G.get_edge(n1,n2)
    - G.edges(), G.edges(n), G.edges(nbunch)      
    - G.edges_iter(), G.edges_iter(n), G.edges_iter(nbunch)
    - G.neighbors(n)
    - G[n]  (equivalent to G.neighbors(n))
    - G.neighbors_iter(n) # iterator over neighbors
    - G.number_of_nodes(), G.order()
    - G.number_of_edges(), G.size()
    - G.degree(n), G.degree(nbunch)
    - G.degree_iter(n), G.degree_iter(nbunch)
    - G.is_directed()
    - G.info()  # print variaous info about a graph
    - G.prepare_nbunch(nbunch)  # return list of nodes in G and nbunch

Methods returning a new graph
-----------------------------

    - G.subgraph(nbunch)
    - G.subgraph(nbunch,create_using=H)
    - G.copy()
    - G.to_undirected()
    - G.to_directed()
    



Implementation Notes
====================

The Graph and DiGraph classes implement graphs using data structures
based on an adjacency list implemented as a node-centric dictionary of
dictionaries. The dictionary contains keys corresponding to the nodes
and the values are dictionaries of neighboring node keys with the
value None (the Python None type).  This allows fast addition,
deletion and lookup of nodes and neighbors in large graphs.  The
underlying datastructure should only be visible in the defining modules. 
In all other modules, instances of graph-like objects are manipulated 
solely via the methods defined by the class and not by acting directly 
on the datastructure.

XGraph and XDiGraph are also implemented using a data structure based on
adjacency lists implemented as a dictionary of dictionaries. The outer
dictionary is keyed by node to an inner dictionary keyed by
neighboring nodes to the edge data/labels/objects (which default to None
to correspond the datastructure used in classes Graph and DiGraph).
If multiedges=True, a list of edge data/labels/objects is stored as
the value of the inner dictionary.  This double dict structure mimics
a sparse matrix and allows fast addition, deletion and lookup of nodes
and neighbors in large graphs.  The underlying datastructure should
only be visible in this module. In all other modules, graph-like
objects are manipulated solely via the methods defined here and not by
acting directly on the datastructure.

Similarities between XGraph and Graph
-------------------------------------

XGraph and Graph differ fundamentally; XGraph edges are 3-tuples
(n1,n2,x) and Graph edges are 2-tuples (n1,n2). XGraph inherits from the
Graph class, and XDiGraph from the DiGraph class.

They do share important similarities.

1. Edgeless graphs are the same in XGraph and Graph.
   For an edgeless graph, represented by G (member of the Graph class)
   and XG (member of XGraph class), there is no difference between
   the datastructures G.adj and XG.adj, other than perhaps the 
   ordering of the keys in the adj dict.

2. Basic graph construction code for G=Graph() will also work for
   G=XGraph().  In the Graph class, the simplest graph construction
   consists of a graph creation command G=Graph() followed by a list
   of graph construction commands, consisting of successive calls to
   the methods:

   G.add_node, G.add_nodes_from, G.add_edge, G.add_edges, G.add_path,
   G.add_cycle G.delete_node, G.delete_nodes_from, G.delete_edge,
   G.delete_edges_from

   with all edges specified as 2-tuples,  

   If one replaces the graph creation command with G=XGraph(), and then
   apply the identical list of construction commands, the resulting XGraph
   object will be a simple graph G with identical datastructure G.adj. 
   This property ensures reuse of code developed for graph generation 
   in the Graph class.


"""
