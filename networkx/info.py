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
   Subclass of Graph.

   An empty digraph is created with

   >>> G=DiGraph()


The XGraph and XDiGraph classes are extensions of the Graph and
DiGraph classes in base.py. The key difference is that an XGraph edge
is a 3-tuple e=(n1,n2,x), representing an undirected edge between
nodes n1 and n2 that is decorated with the object x. Here n1 and n2
are (hashable) node objects and x is a (not necessarily hashable) edge
object. Since the edge is undirected, edge (n1,n2,x) is equivalent to
edge (n2,n1,x).

An XDiGraph edge is a similar 3-tuple e=(n1,n2,x), with the additional
property of directedness. I.e. e=(n1,n2,x) is a directed edge from n1 to
n2 decorated with the object x, and is not equivalent to the edge (n2,n1,x).

Whether a graph or digraph allow self-loops or multiple edges is
determined at the time of object instantiation via specifying the
parameters selfloops=True/False and multiedges=True/False. For
example, an empty XGraph is created with:

>>> G=XGraph()

which is equivalent to

>>> G=XGraph(name="No Name", selfloops=False, multiedges=False)

and similarly for XDiGraph.

>>> G=XDiGraph(name="empty", multiedges=True)

creates an empty digraph G with G.name="empty", that do not
allow the addition of selfloops but do allow for multiple edges.


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
   an nbunch is any iterable (non-string) container 
   of nodes that is not itself a node of the graph.

e=(n1,n2):
   an edge (a python "2-tuple"), also written n1-n2 (if undirected)
   and n1->n2 (if directed). Note that 3-tuple edges of the form
   (n1,n2,x) are used in the XGraph and XDiGraph classes. If G is an
   XGraph, then G.add_edge(n1,n2) will add the edge (n1,n2,None), and
   G.delete_edge(n1,n2) will attempt to delete the edge (n1,n2,None).
   In the case of multiple edges between nodes n1 and n2, one can use
   G.delete_multiedge(n1,n2) to delete all edges between n1 and n2.

e=(n1,n2,x):
   an edge triple ("3-tuple") containing the two nodes connected and the 
   edge data/label/object stored associated with the edge. The object x,
   or a list of objects (if multiedges=True), can be obtained using
   G.get_edge(n1,n2)

elist:
   a list of edges (as 2- or 3-tuples)

ebunch:
   a bunch of edges (as 2- or 3-tuples)
   an ebunch is any iterable (non-string) container
   of edge-tuples (either 2-tuples, 3-tuples or a mixture).
   (similar to nbunch, also see add_edge).

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
    - n in G (equivalent to G.has_node(n))
    - G.has_node(n)
    - G.nodes()
    - G.nodes_iter()
    - G.has_edge(n1,n2)
    - G.edges(), G.edges(n), G.edges(nbunch)      
    - G.edges_iter(), G.edges_iter(n), G.edges_iter(nbunch)
    - G.neighbors(n)
    - G[n]  (equivalent to G.neighbors(n))
    - G.neighbors_iter(n) # iterator over neighbors
    - G.number_of_nodes()
    - G.number_of_edges()
    - G.degree(n), G.degree(nbunch)
    - G.degree_iter(n), G.degree_iter(nbunch)
    - G.is_directed()

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
underlying datastructure should only be visible in this module. In all
other modules, instances of graph-like objects are manipulated solely
via the methods defined here and not by acting directly on the
datastructure.

XGraph and XDiGraph are implemented using a data structure based on an
adjacency list implemented as a dictionary of dictionaries. The outer
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
   the datastructures G.adj and XG.adj, other than in the ordering of the
   keys in the adj dict.

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
   object will be a simple graph G with identical datastructure G.adj. This
   property ensures reuse of code developed for graph generation in the
   Graph class.


"""
