..  -*- coding: utf-8 -*-

********
Tutorial
********

Introduction
============
NetworkX is a Python-based package for the creation, manipulation, and
study of the structure, dynamics, and function of complex networks. The
name means **Network "X"** and we pronounce it **NX**. We often 
will shorten NetworkX to "nx" in code examples by using the
Python import 

>>> import networkx as nx

The structure of a graph or network is encoded in the **edges**
(connections, links, ties, arcs, bonds) between **nodes** (vertices,
sites, actors). If unqualified, by graph we mean an undirected
graph, i.e. no multiple edges are allowed. By a network we usually 
mean a graph with weights (fields, properties) on nodes and/or edges.

The potential audience for NetworkX include: mathematicians,
physicists, biologists, computer scientists, social scientists. The
current state of the art of the (young and rapidly growing) science of
complex networks is presented in Albert and Barabási [BA02]_, Newman
[Newman03]_, and Dorogovtsev and Mendes [DM03]_. See also the classic
texts [Bollobas01]_, [Diestel97]_ and [West01_] for graph theoretic
results and terminology. For basic graph algorithms, we recommend the
texts of Sedgewick, e.g. [Sedgewick01]_ and [Sedgewick02]_ and the
modern survey of Brandes and Erlebach [BE05]_.
  
Why Python? Past experience showed this approach to maximize
productivity, power, multi-disciplinary scope (our application test
beds included large communication, social, data and biological
networks), and platform independence. This philosophy does not exclude
using whatever other language is appropriate for a specific subtask,
since Python is also an excellent "glue" language [Langtangen04]_. 
Equally important, Python is free, well-supported and a joy to use. 
Among the many guides to Python, we recommend the documentation at
http://www.python.org and the text by Alex Martelli [Martelli03]_.

NetworkX is free software; you can redistribute it and/or
modify it under the terms of the **LGPL** (GNU Lesser General Public
License) as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.
Please see the license for more information. 

Obtaining and Installing NetworkX
==================================

You need Python. We recommend the latest stable release available
from http://www.python.org/.  NetworkX requires 
Python Release 2.4 or later. 

The latest version of NetworkX can be found at
http://networkx.lanl.gov/
 
NetworkX will work on multiple platforms.

On Linux platforms, download the current tarball numbered, say,
networkx-x.xx.tar.gz, to an appropriate directory, say /home/username/networks

::

   gzip -d -c networkx-x.xx.tar.gz|tar xvf-
   cd networkxx-x.xx
   # run the following with your preferred Python version
   python setup.py build
   # change to a user id that is allowed to do installation
   python setup.py install

This will install NetworkX in your Python site-packages directory.

If you don't have permission to install software on your
system, you can install into another directory using
the --prefix or --home flags to setup.py.

For example

::  

    python setup.py install --prefix=/home/username/python
    or
    python setup.py install --home=~

If you didn't install in the standard Python site-packages directory
you will need to set your PYTHONPATH variable to the alternate location.
See http://docs.python.org/inst/search-path.html for further details.


A Quick Tour
============

Building and drawing a small graph
----------------------------------

We assume you can start an interactive Python session..
We will assume that you are familiar with Python terminology 
(see the official Python website http://www.python.org for more
information).

::

  %python
  ...
  Some lines giving information such as the version of python and compiler used.
  ...
  Type "help", "copyright", "credits" or "license" for more information.
  >>>

(If you did not install NX into the Python site directory 
it might be useful to add the directory where NX is installed to
your PYTHONPATH.)

After starting Python, import the networkx module with (the recommended way)

>>> import networkx as nx

To save repetition, in all the examples below we assume that 
NX has been imported this way.

You may also use the usual mode for interactive experimentation that might
clobber some names already in your namespace

>>> from networkx import *

If importing networkx fails, it means that Python cannot find the installed
module. Check your installation and your PYTHONPATH.

To create a new graph, call Graph() with zero or more arguments.

>>> G=nx.Graph()

When called with zero arguments, one obtains the empty graph without
any nodes or edges.  In NX every graph or network is a Python
"object", and in Python the functions associated with an "object" are
known as methods.

The following classes are provided:

Graph
   The basic operations common to graph-like classes.
   This class implements an undirected graph. It ignores
   multiple edges between two nodes.  It does allow self-loop
   edges between a node and itself.

DiGraph
   Operations common to directed graphs, that is, graphs with directed edges.
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

All graph classes allow any hashable object as a node and arbitrary 
edge data/weights/labels to be associated with an edge.  

All graph classes have boolean attributes to describe the nature of the
graph:  directed, weighted, multiedges.
The weighted attribute means that the edge weights are numerical, though
that is not enforced.  Some functions will not work on graphs that do
not have weighted==True (the default), so it can be used to protect yourself
against using a routine that requires numerical edge data.

This package implements graphs using data structures based on an
adjacency list implemented as a node-centric dictionary of
dictionaries. The outer dictionary is keyed by nodes to values that are
themselves dictionaries keyed by neighboring node to the
edge object (default 1) associated with that edge (or a list of edge
objects for MultiGraph/MultiDiGraph).  This 'dict-of-dicts' structure
allows fast addition, deletion and lookup of nodes and neighbors in 
large graphs.  The underlying datastructure is accessed directly 
by methods (the API) in the class definitions.  
All functions, on the other hand, manipulate graph-like objects 
solely via those API methods and not by acting directly on the datastructure. 
This design allows for possible replacement of the 'dicts-of-dicts"-based 
datastructure with an alternative datastructure without excessive effort.

Glossary
--------

The following shorthand is used throughout NetworkX documentation and code:
 
G,G1,G2,H,etc
   Graphs

n,n1,n2,u,v,v1,v2:
   nodes (vertices)

nlist,vlist:
   a list of nodes (vertices)

nbunch, vbunch:
   a "bunch" of nodes (vertices).
   An nbunch is any iterable container
   of nodes that is not itself a node in the graph. (It can be an
   iterable or an iterator, e.g. a list, set, graph, file, etc..)

e=(n1,n2), (n1,n2,x):
   an edge (a Python 2-tuple or 3-tuple),
   also written n1-n2 (if undirected) and n1->n2 (if directed).
 
e=(n1,n2,x): 
   The edge object x (or list of objects for multigraphs) associated 
   with an edge can be obtained using G.get_edge(n1,n2). 
   The default G.add_edge(n1,n2) is equivalent to G.add_edge(n1,n2,1). 
   In the case of multiple edges in multigraphs between nodes n1 and n2, 
   one can use G.remove_edge(n1,n2) to remove all edges between n1 and n2, or
   G.remove_edge(n1,n2,x) to remove one edge associated with object x. 

elist:
   a list of edges (as 2- or 3-tuples)

ebunch:
   a bunch of edges (as tuples)
   an ebunch is any iterable (non-string) container
   of edge-tuples. (Similar to nbunch, also see add_edge).

function/method names:
   There are many ways you might want to return node properties for all nodes.
   For example degree, clustering or betweenness are node properties.
   NX provides functions which return node properties as a list, an iterator, 
   a dict keyed by node to the property value or 2-tuples (node, property value).  
   For example, clustering(G) returns a list of clustering values, 
   clustering_iter(G) returns an iterator over the values.  
   Both forms take the optional argument with_labels (default False).
   clustering(G,with_labels=True) returns a dict keyed by node to the clustering value.
   clustering_iter(G,with_labels=True) returns an iterator over 2-tuples (node,clustering value).
   These two names and the with_labels keyword should be available for any node 
   property by substituting the property name for "clustering" in these examples. 


Warning:
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
    - G[n]               # dict of neighbors of n keyed to edge object
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
(On linux machines with CPython the hexadecimal address is the memory
location of the object.) 

Examples
========

Create an empty graph with zero nodes and zero edges.

>>> G=nx.Graph()

G can be grown in several ways.
By adding one node at a time,

>>> G.add_node(1)

by adding a list of nodes,

>>> G.add_nodes_from([2,3])

or by adding any nbunch of nodes (see above definition of an nbunch),

>>> H=nx.path_graph(10)
>>> G.add_nodes_from(H)

(H can be a graph, iterator,  string,  set, or even a file.)

Any hashable object (except None) can represent a node, e.g. a text string, an
image, an XML object, another Graph, a customized node object, etc.

>>> G.add_node(H)

(You should not change the object if the hash depends on its contents.)

G can also be grown by adding one edge at a time,

>>> G.add_edge( (1,2) )

by adding a list of edges, 

>>> G.add_edges_from([(1,2),(1,3)])

or by adding any ebunch of edges (see above definition of an ebunch),

>>> G.add_edges_from(H.edges())

One can demolish the graph in a similar fashion; using remove_node,
remove_nodes_from, remove_edge and remove_edges_from, e.g.

>>> G.remove_node(H)

There are no complaints when adding existing nodes or edges. For example,
after removing all nodes and edges,

>>> G.clear()
>>> G.add_edges_from([(1,2),(1,3)])
>>> G.add_node(1)
>>> G.add_edge((1,2))
>>> G.add_node("spam")

will add new nodes/edges as required and stay quiet if they are
already present.

>>> G.add_node("spam")       # adds node "spam"
>>> G.add_nodes_from("spam") # adds 4 nodes: 's', 'p', 'a', 'm'

At this stage the graph G consists of 8 nodes and 2 edges, as can be seen by:

>>> number_of_nodes(G)
8
>>> number_of_edges(G)
2

We can examine them with

>>> G.nodes()
[1, 2, 3, 'spam', 's', 'p', 'a', 'm']
>>> G.edges()
[(1, 2), (1, 3)]

Removing nodes is similar:

>>> G.remove_nodes_from("spam")
>>> G.nodes()
[1, 2, 3, 'spam']

You can specify graph data upon instantiation if an appropriate structure exists.

>>> H=nx.DiGraph(G)   # create a DiGraph with connection data from G
>>> H.edges()
[(1, 2), (1, 3), (2, 1), (3, 1)]
>>> H=nx.Graph( {0: [1,2,3], 1: [0,3], 2: [0], 3:[0]} )  # a dict of lists adjacency

Edge data/weights/labels/objects can also be associated with an edge:

>>> H=nx.Graph()
>>> H.add_edge(1,2,"red")
>>> H.add_edges_from([(1,3,"blue"), (2,0,"red"), (0,3)])
>>> H.edges()
[(0, 2), (1, 2), (1, 3)]
>>> H.edges(data=True)
[(0, 2, 1), (1, 2, "red"), (1, 3, "blue")]

Arbitrary objects can be associated with an edge.  The 3-tuples (n1,n2,x)
represent an edge between nodes n1 and n2 that is decorated with
the object x (not necessarily hashable).  For example, n1 and n2 can be
protein objects from the RCSB Protein Data Bank, and x can refer to an XML
record of a publication detailing experimental observations of their
interaction. 

You can see that while NX has not implemented either nodes or edges as 
networkx classes.  This leaves you free to use your existing node and edge
objects, or more typically, use numerical values or strings where appropriate.
A node can be any hashable object (except None), and an edge can be associated 
with any object x using G.add_edge(n1,n2,x).


Drawing a small graph
---------------------

NetworkX is not primarily a graph drawing package but 
basic drawing with Matplotlib as well as an interface to use the
open source Graphviz software package are included.  
These reside in networkx.drawing,
and will be imported if possible. See the drawing section for details.

First import Matplotlib's plot interface

>>> import matplotlib.pyplot as plt

To test if the import of networkx.drawing was successful 
draw G using one of

>>> nx.draw(G)
>>> nx.draw_random(G)
>>> nx.draw_circular(G)
>>> nx.draw_spectral(G)

when drawing to an interactive display. 
Note that you may need to issue a Matplotlib 

>>> plt.show() 

command if you are not using matplotlib in interactive mode
http://matplotlib.sourceforge.net/faq/installing_faq.html#matplotlib-compiled-fine-but-nothing-shows-up-with-plot

Or use

>>> nx.draw(G)
>>> plt.savefig("path.png")

to write to the file "path.png" in the local directory. If graphviz
and pygraphviz or pydot are available on your system, you can also use

>>> nx.draw_graphviz(G)
>>> nx.write_dot(G,'file.dot')

You may find it useful to interactively test code using "ipython -pylab", 
which combines the power of ipython and matplotlib.

Functions for analyzing graph properties
----------------------------------------

The structure of G can be analyzed using various graph
theoretic functions such as:
 
>>> nx.connected_components(G)
[[1, 2, 3], ['spam']]

>>> sorted(nx.degree(G))
[0, 1, 1, 2]

>>> nx.clustering(G)
[0.0, 0.0, 0.0, 0.0]

Some functions defined on the nodes, e.g. degree() and clustering(), can
be given a single node or an nbunch of nodes as argument. If a single node is
specified, then a single value is returned. If an iterable nbunch is
specified, then the function will return a list of values. With no argument, 
the function will return a list of values at all nodes of the graph.
 
>>> degree(G,1)
2
>>> G.degree(1)
2

>>> sorted(G.degree([1,2]))
[1, 2]

>>> sorted(G.degree())
[0, 1, 1, 2]

The keyword argument with_labels=True returns a dict keyed by nodes
to the node values.

>>> G.degree([1,2],with_labels=True)
{1: 2, 2: 1}
>>> G.degree(with_labels=True)
{1: 2, 2: 1, 3: 1, 'spam': 0}



Graph generators and graph operations
-------------------------------------

In addition to constructing graphs node-by-node or edge-by-edge, they
can also be generated by:

1. Applying classic graph operations, such as::

    subgraph(G, nbunch)      - induce subgraph of G on nodes in nbunch
    union(G1,G2)             - graph union
    disjoint_union(G1,G2)    - graph union assuming all nodes are different
    cartesian_product(G1,G2) - return Cartesian product graph
    compose(G1,G2)           - combine graphs identifying nodes common
                               to both
    complement(G)            - graph complement 
    create_empty_copy(G)     - return an empty copy of the same graph class
    convert_to_undirected(G) - return an undirected representation of G
    convert_to_directed(G)   - return a directed representation of G


2. Using a call to one of the classic small graphs, e.g.

>>> petersen=nx.petersen_graph()
>>> tutte=nx.tutte_graph()
>>> maze=nx.sedgewick_maze_graph()
>>> tet=nx.tetrahedral_graph()

3. Using a (constructive) generator for a classic graph, e.g.

>>> K_5=nx.complete_graph(5)
>>> K_3_5=nx.complete_bipartite_graph(3,5)
>>> barbell=nx.barbell_graph(10,10)
>>> lollipop=nx.lollipop_graph(10,20)
 
4. Using a stochastic graph generator, e.g.

>>> er=nx.erdos_renyi_graph(100,0.15)
>>> ws=nx.watts_strogatz_graph(30,3,0.1)
>>> ba=nx.barabasi_albert_graph(100,5)
>>> red=nx.random_lobster(100,0.9,0.9)


Graph IO
========

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
build Euler's famous graph of the bridges of Konigsberg over 
the Pregel river, one can use:

>>> K=nx.MultiGraph(name="Konigsberg")
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

NetworkX provides interfaces to matplotlib and graphviz for graph
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



References
==========

.. [BA02] R. Albert and A.-L. Barabási, "Statistical mechanics of complex
   networks", Reviews of Modern Physics, 74, pp. 47-97, 2002.
   (Preprint available online at http://citeseer.ist.psu.edu/442178.html
   or http://arxiv.org/abs/cond-mat/0106096)


.. [Bollobas01] B. Bollobás, "Random Graphs", Second Edition,
   Cambridge University Press, 2001.

.. [BE05] U. Brandes and T. Erlebach, "Network Analysis:
   Methodological Foundations", Lecture Notes in Computer Science, 
   Volume 3418, Springer-Verlag, 2005.

.. [Diestel97] R. Diestel, "Graph Theory", Springer-Verlag, 1997.
   (A free electronic version is available at
   http://www.math.uni-hamburg.de/home/diestel/books/graph.theory/download.html)


.. [DM03] S.N. Dorogovtsev and J.F.F. Mendes, "Evolution of Networks",
   Oxford University Press, 2003.


.. [Langtangen04] H.P. Langtangen, "Python Scripting for Computational
    Science.", Springer Verlag Series in Computational Science and
    Engineering, 2004. 


.. [Martelli03]  A. Martelli, "Python in a Nutshell", O'Reilly Media
   Inc, 2003. (A useful guide to the language is available at 
   http://www.oreilly.com/catalog/pythonian/chapter/ch04.pdf)


.. [Newman03] M.E.J. Newman, "The Structure and Function of Complex
   Networks", SIAM Review, 45, pp. 167-256, 2003. (Available online at 
   http://epubs.siam.org/sam-bin/dbq/article/42480 ) 


.. [Sedgewick02] R. Sedgewick, "Algorithms in C: Parts 1-4: 
   Fundamentals, Data Structure, Sorting, Searching", Addison Wesley
   Professional, 3rd ed., 2002.


.. [Sedgewick01] R. Sedgewick, "Algorithms in C, Part 5: Graph Algorithms",
   Addison Wesley Professional, 3rd ed., 2001.


.. [West01] D. B. West, "Introduction to Graph Theory", Prentice Hall,
    2nd ed., 2001.  

