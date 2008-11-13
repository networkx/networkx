..  -*- coding: utf-8 -*-
A Quick Tour
============

Building and drawing a small graph
----------------------------------

We assume you can start an interactive Python session..
We will assume that you are familiar with Python terminology 
(see the official Python website http://www.python.org for more
information).
If you did not install NetworkX into the Python site directory 
it might be useful to add that directory to your PYTHONPATH.

After starting Python, import the networkx module with (the recommended way)

>>> import networkx as nx

To save repetition, in all the examples below we assume that 
NX has been imported this way.

You may also use the usual mode for interactive experimentation that might
clobber some names already in your name-space

>>> from networkx import *

If importing networkx fails, it means that Python cannot find the installed
module. Check your installation and your PYTHONPATH.

The following basic graph types are provided as Python classes:

Graph
   This class implements an undirected graph. It ignores
   multiple edges between two nodes.  It does allow self-loop
   edges between a node and itself.

DiGraph
   Directed graphs, that is, graphs with directed edges.
   Operations common to directed graphs, 
   (A subclass of Graph.)

MultiGraph
   A flexible graph class that allows multiple undirected edges between 
   pairs of nodes.  The additional flexibility leads to some degradation 
   in performance, though usually not significant.
   (A subclass of Graph.)

MultiDiGraph
   A directed version of a MultiGraph.  
   (A subclass of DiGraph.)

Empty graph-like objects are created with

>>> G=nx.Graph()
>>> G=nx.DiGraph()
>>> G=nx.MultiGraph()
>>> G=nx.MultiDiGraph()

When called with no arguments you get a graph without
any nodes or edges (empty graph).  In NX every graph or network is a Python
"object", and in Python the functions associated with an "object" are
known as methods.

All graph classes allow any hashable object as a node.   Hashable
objects include strings, tuples, integers, and more.
Arbitrary edge data/weights/labels can be associated with an edge.  

All graph classes have boolean attributes to describe the nature of the
graph:  directed, weighted, multigraph.
The weighted attribute means that the edge weights are numerical, though
that is not enforced.  Some functions will not work on graphs that do
not have weighted==True (the default), so it can be used to protect yourself
against using a routine that requires numerical edge data.

The graph classes data structures are based on an
adjacency list and implemented as a Python dictionary of
dictionaries. The outer dictionary is keyed by nodes to values that are
themselves dictionaries keyed by neighboring node to the
edge object (default 1) associated with that edge (or a list of edge
objects for MultiGraph/MultiDiGraph).  This "dict-of-dicts" structure
allows fast addition, deletion, and lookup of nodes and neighbors in 
large graphs.  The underlying datastructure is accessed directly 
by methods (the programming interface "API") in the class definitions.  
All functions, on the other hand, manipulate graph-like objects 
solely via those API methods and not by acting directly on the datastructure. 
This design allows for possible replacement of the 'dicts-of-dicts'-based 
datastructure with an alternative datastructure that implements the
same methods.

Glossary
--------

The following shorthand is used throughout NetworkX documentation and code:
 
G,G1,G2,H,etc
   Graphs

n,n1,n2,u,v,v1,v2:
   Nodes (vertices)

nlist,vlist:
   A list of nodes (vertices)

nbunch, vbunch:
   A "bunch" of nodes (vertices).
   An nbunch is any iterable container
   of nodes that is not itself a node in the graph. (It can be an
   iterable or an iterator, e.g. a list, set, graph, file, etc..)

e=(n1,n2), (n1,n2,x):
   An edge (a Python 2-tuple or 3-tuple),
   also written n1-n2 (if undirected) and n1->n2 (if directed).
 
e=(n1,n2,x): 
   The edge object x (or list of objects for multigraphs) associated 
   with an edge can be obtained using G.get_edge(n1,n2). 
   The default G.add_edge(n1,n2) is equivalent to G.add_edge(n1,n2,1). 
   In the case of multiple edges in multigraphs between nodes n1 and n2, 
   one can use G.remove_edge(n1,n2) to remove all edges between n1 and n2, or
   G.remove_edge(n1,n2,x) to remove one edge associated with object x. 

elist:
   A list of edges (as 2- or 3-tuples)

ebunch:
   A bunch of edges (as tuples).
   An ebunch is any iterable (non-string) container
   of edge-tuples. (Similar to nbunch, also see add_edge).

iterator method names:
   In many cases it is more efficient to iterate through items rather
   than creating a list of items.  
   NetworkX provides separate methods that return an iterator.  
   For example, G.degree() and G.edges() return lists while G.degree_iter() 
   and G.edges_iter() return iterators.


Some potential pitfalls to be aware of:

  - Although any hashable object can be used as a node, one should not
    change the object after it has been added as a
    node (since the hash can depend on the object contents).
  - The ordering of objects within an arbitrary nbunch/ebunch
    can be machine- or implementation-dependent.
  - Algorithms applicable to arbitrary nbunch/ebunch should treat 
    them as once-through-and-exhausted iterable containers.
  - len(nbunch) and len(ebunch) need not be defined.    



Graph methods
-------------

A Graph object G has the following primitive methods associated
with it. (You can use dir(G) to inspect the methods associated with object G.)

1. Non-mutating Graph methods::

    - len(G), G.number_of_nodes(), G.order()  # number of nodes in G
    - n in G,     G.has_node(n)       
    - for n in G:   # loop through the nodes in G
    - for nbr in G[n]:  # loop through the neighbors of n in G
    - G.nodes()        # list of nodes
    - G.nodes_iter()   # iterator over nodes
    - nbr in G[n],  G.has_edge(n1,n2), G.has_neighbor(n1,n2)
    - G.edges(), G.edges(n), G.edges(nbunch)      
    - G.edges_iter(), G.edges_iter(n), G.edges_iter(nbunch)
    - G.get_edge(n1,n2)  # the object associated with this edge
    - G.neighbors(n)     # list of neighbors of n
    - G.neighbors_iter(n) # iterator over neighbors
    - G[n]               # dictionary of neighbors of n keyed to edge object
    - G.adjacency_list  #list of 
    - G.number_of_edges(), G.size()
    - G.degree(), G.degree(n), G.degree(nbunch)
    - G.degree_iter(), G.degree_iter(n), G.degree_iter(nbunch)
    - G.nodes_with_selfloops()
    - G.selfloop_edges()
    - G.number_of_selfloops()
    - G.nbunch_iter(nbunch)  # iterator over nodes in both nbunch and G

    The following return a new graph::

    - G.subgraph(nbunch,copy=True)
    - G.copy() 
    - G.to_directed()
    - G.to_undirected()
    
2. Mutating Graph methods::

    - G.add_node(n), G.add_nodes_from(nbunch)
    - G.remove_node(n), G.remove_nodes_from(nbunch)
    - G.add_edge(n1,n2), G.add_edge(*e)
    - G.add_edges_from(ebunch)
    - G.remove_edge(n1,n2), G.remove_edge(*e), 
    - G.remove_edges_from(ebunch)
    - G.add_star(nlist)
    - G.add_path(nlist)
    - G.add_cycle(nlist)
    - G.clear()
    - G.subgraph(nbunch,copy=False)


Names of classes/objects use the CapWords convention,
e.g. Graph, MultiDiGraph. Names of functions and methods
use the lowercase_words_separated_by_underscores convention,
e.g. petersen_graph(), G.add_node(10).

G can be inspected interactively by typing "G" (without the quotes).
This will reply something like <networkx.base.Graph object at 0x40179a0c>.
(On Linux machines with CPython the hexadecimal address is the memory
location of the object.) 

