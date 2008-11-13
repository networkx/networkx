..  -*- coding: utf-8 -*-
Graph IO
========

NetworkX can read and write graphs in many formats.  See
http://networkx.lanl.gov/reference/readwrite.html for
a complete list of currently supported formats.

Reading a graph from a file
---------------------------

>>> G=nx.tetrahedral_graph()

Write to adjacency list format

>>> nx.write_adjlist(G, "tetrahedral.adjlist")

Read from adjacency list format

>>> H=nx.read_adjlist("tetrahedral.adjlist")

Write to edge list format

>>> nx.write_edgelist(G, "tetrahedral.edgelist")

Read from edge list format

>>> H=nx.read_edgelist("tetrahedral.edgelist")


See also `Interfacing with other tools`_ below for
how to draw graphs with matplotlib or graphviz.

Graphs with multiple edges
==========================

See the MultiGraph and MultiDiGraph classes. For example, to 
build Euler's famous graph of the bridges of Königsberg over 
the Pregel river, one can use 
 
>>> K=nx.MultiGraph(name="Königsberg")
>>> K.add_edges_from([("A","B","Honey Bridge"),
...                   ("A","B","Blacksmith's Bridge"),
...                   ("A","C","Green Bridge"),
...                   ("A","C","Connecting Bridge"),
...                   ("A","D","Merchant's Bridge"),
...                   ("C","D","High Bridge"),
...                   ("B","D","Wooden Bridge")])
>>> K.degree("A")
5

Directed Graphs
===============

The DiGraph class provides operations common to digraphs (graphs with
directed edges). A subclass of Graph, Digraph adds the following
methods to those of Graph:

    - out_edges
    - out_edges_iter
    - in_edges
    - in_edges_iter
    - has_successor=has_neighbor
    - has_predecessor
    - successors=neighbors
    - successors_iter=neighbors_iter
    - predecessors
    - predecessors_iter
    - out_degree
    - out_degree_iter
    - in_degree
    - in_degree_iter
    - reverse

See networkx.DiGraph for more documentation. 


Interfacing with other tools
============================

NetworkX provides interfaces to Matplotlib and Graphviz for graph
layout (node and edge positioning) and drawing. We also use matplotlib for 
graph spectra and in some drawing operations. Without either, one can
still use the basic graph-related functions.

See the graph drawing section for details on how to install and use 
these tools.

Matplotlib
----------

>>> G=nx.tetrahedral_graph()
>>> nx.draw(G)  


Graphviz
--------

>>> G=nx.tetrahedral_graph()
>>> nx.write_dot(G,"tetrahedral.dot")


Specialized Topics
==================

Graphs composed of general objects
----------------------------------

For most applications, nodes will have string or integer labels.
The power of Python ("everything is an object") allows us to construct 
graphs with ANY hashable object as a node. 
(The Python object None is not allowed as a node). 
Note however that this will not work with non-Python
datastructures, e.g. building a graph on a wrapped Python version
of graphviz).

For example, one can construct a graph with Python
mathematical functions as nodes, and where two mathematical
functions are connected if they are in the same chapter in some
Handbook of Mathematical Functions. E.g.

>>> from math import *
>>> G=nx.Graph()
>>> G.add_node(acos)
>>> G.add_node(sinh)
>>> G.add_node(cos)
>>> G.add_node(tanh)
>>> G.add_edge(acos,cos)
>>> G.add_edge(sinh,tanh)
>>> sorted(G.nodes())
[<built-in function acos>, <built-in function cos>, <built-in function sinh>, <built-in function tanh>]

As another example, one can build (meta) graphs using other graphs as
the nodes.

We have found this power quite useful, but its abuse
can lead to unexpected surprises unless one is familiar with Python. If
in doubt, consider using convert_node_labels_to_integers() to obtain
a more traditional graph with integer labels.


