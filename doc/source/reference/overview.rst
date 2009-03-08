Overview
~~~~~~~~
NetworkX provides data structures for graphs (or networks)
along with graph algorithms, generators, and drawing tools.

Graphs
=======
Simple graphs, graphs with a maximum of one undirected edge between
any two nodes, are stored in NetworkX with the Graph class.  Other
classes allow directed graphs (DiGraph) and multiple edges
(MultiGraph/MultiDiGraph).  

Simple graphs are constructed by creating a Graph() object.

>>> import networkx as nx
>>> G=nx.Graph()

At this point, the graph G has no nodes or edges and the
name is the empty string.  Optional arguments to the graph constructor
allow building the graph from existing data structures or providing
a name

>>> G=nx.Graph(name="My Graph")
>>> print G.name
My Graph

Graph Manipulation
==================

Basic graph operations are provided through methods to add or 
remove nodes or edges.

>>> G.add_node(1)
>>> G.add_nodes_from(["red","blue","green"])
>>> G.remove_node(1)
>>> G.remove_nodes_from(["red","blue","green"])
>>> G.add_edge(1,2)
>>> G.add_edges_from([(1,3),(1,4)])
>>> G.remove_edge(1,2)
>>> G.remove_edges_from([(1,3),(1,4)])


If a node is removed, all edges associated with that node are also
removed.  If an edge is added connecting a node that does not yet
exist, that node is added when the edge is added.

More complex manipulation is available through the methods::

    G.add_star([list of nodes])   - add edges from the first node to all other nodes.
    G.add_path([list of nodes])   - add edges to make this ordered path.
    G.add_cycle([list of nodes])  - same as path, but connect ends.
    G.subgraph([list of nodes]) - the subgraph of G containing those nodes.
    G.clear()   - remove all nodes and edges.
    G.copy()    - a copy of the graph.  
    G.to_undirected()  - return an undirected representation of G
    G.to_directed()    - return a directed representation of G
    
Note: For G.copy() the graph structure is copied, but the nodes and edge data 
point to the same objects in the new and old graph.

In addition, the following functions are available::

    union(G1,G2)             - graph union 
    disjoint_union(G1,G2)    - graph union assuming all nodes are different
    cartesian_product(G1,G2) - return Cartesian product graph
    compose(G1,G2)           - combine graphs identifying nodes common to both
    complement(G)            - graph complement 
    create_empty_copy(G)     - return an empty copy of the same graph class

You should also look at the graph generation routines in networkx.generators

Methods
=======

Some properties are tied more closely to the data structure and can be
obtained through methods as well as functions.  These are::

 - G.number_of_nodes()
 - G.number_of_edges()
 - G.nodes()        - a list of nodes in G.
 - G.nodes_iter()   - an iterator over the nodes of G.
 - G.has_node(v)    - check if node v in G (returns True or False).
 - G.edges()        - a list of 2-tuples specifying edges of G.
 - G.edges_iter()   - an iterator over the edges (as 2-tuples) of G.
 - G.has_edge(u,v)  - check if edge (u,v) in G (returns True or False).
 - G.neighbors(v)   - list of the neighbors of node v (outgoing if directed).
 - G.neighbors_iter(v)     - an iterator over the neighbors of node v.
 - G.degree()       - list of the degree of each node.
 - G.degree_iter()  - an iterator yielding 2-tuples (node, degree).

Argument syntax and options are the same as for the functional form.

Node/Edge Reporting Methods
===========================

In many cases it is more efficient to loop using an iterator directly rather
than creating a list.  NX provides separate methods that return an iterator.  
For example, G.degree() and G.edges() return lists while G.degree_iter() 
and G.edges_iter() return iterators.  The suffix "_iter"
in a method name signifies that an iterator will be returned.

For node properties, an optional argument "with_labels" signifies whether the
returned values should be identified by node or not. 
If "with_labels=False", only property values are returned.
If "with_labels=True", a dict keyed by node to the property values is returned.

The following examples use the "triangles" function which returns 
the number of triangles a given node belongs to.

Example usage

>>> G=nx.complete_graph(4)	
>>> print G.nodes()
[0, 1, 2, 3]
>>> print nx.triangles(G)                 
[3, 3, 3, 3]
>>> print nx.triangles(G,with_labels=True)    
{0: 3, 1: 3, 2: 3, 3: 3}

Properties for specific nodes
=============================

Many node property functions return property values for either 
a single node, a list of nodes, or the whole graph.
The return type is determined by an optional input argument.

1. By default, values are returned for all nodes in the graph.
2. If input is a list of nodes, a list of values for those nodes is returned.
3. If input is a single node, the value for that node is returned.

Node v is special for some reason.  We want to print info on it.


>>> v=1
>>> print "Node %s has %s triangles."%(v,nx.triangles(G,v))
Node 1 has 3 triangles.

Maybe you need a polynomial on t?

>>> t=nx.triangles(G,v)
>>> poly=t**3+2*t-t+5

Get triangles for a subset of all nodes.

>>> vlist=range(0,4)
>>> triangle_dict = nx.triangles(G,vlist,with_labels=True)
>>> for (v,t) in triangle_dict.items():
...     print "Node %s is part of %s triangles."%(v,t)
Node 0 is part of 3 triangles.
Node 1 is part of 3 triangles.
Node 2 is part of 3 triangles.
Node 3 is part of 3 triangles.
