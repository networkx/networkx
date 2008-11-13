..  -*- coding: utf-8 -*-

Examples
========

Create an empty graph with no nodes and no edges.

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

>>> G.add_edge(1,2)

or

>>> e=(2,3)
>>> G.add_edge(*e) # unpack edge tuple

or by adding a list of edges, 

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
>>> G.add_edge(1,2)
>>> G.add_node("spam")       # adds node "spam"
>>> G.add_nodes_from("spam") # adds 4 nodes: 's', 'p', 'a', 'm'

will add new nodes/edges as required and stay quiet if they are
already present.

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
>>> H.add_edge(1,2,'red')
>>> H.add_edges_from([(1,3,'blue'), (2,0,'red'), (0,3)])
>>> H.edges()
[(0, 2), (0, 3), (1, 2), (1, 3)]
>>> H.edges(data=True)
[(0, 2, 'red'), (0, 3, 1), (1, 2, 'red'), (1, 3, 'blue')]

Arbitrary objects can be associated with an edge.  The 3-tuples (n1,n2,x)
represent an edge between nodes n1 and n2 that is decorated with
the object x (not necessarily hashable).  For example, n1 and n2 can be
protein objects from the RCSB Protein Data Bank, and x can refer to an XML
record of a publication detailing experimental observations of their
interaction. 

You can see that nodes and edges are not
NetworkX classes.  This leaves you free to use your existing node and edge
objects, or more typically, use numerical values or strings where appropriate.
A node can be any hashable object (except None), and an edge can be associated 
with any object x using G.add_edge(n1,n2,x).

Drawing a small graph
---------------------

NetworkX is not primarily a graph drawing package but 
basic drawing with Matplotlib as well as an interface to use the
open source Graphviz software package are included.  
These are part of the networkx.drawing package
and will be imported if possible. See the drawing section for details.

First import Matplotlib's plot interface (pylab works too)

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

You may find it useful to interactively test code using "ipython -pylab", 
which combines the power of ipython and matplotlib and provides a convenient
interactive mode.

Or to save drawings to a file, use, for example

>>> nx.draw(G)
>>> plt.savefig("path.png")

to write to the file "path.png" in the local directory. If Graphviz
and PyGraphviz, or pydot, are available on your system, you can also use

>>> nx.draw_graphviz(G)
>>> nx.write_dot(G,'file.dot')

Functions for analyzing graph properties
----------------------------------------

The structure of G can be analyzed using various graph-theoretic 
functions such as:
 
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
can also be generated by

1. Applying classic graph operations, such as::

    subgraph(G, nbunch)      - induce subgraph of G on nodes in nbunch
    union(G1,G2)             - graph union
    disjoint_union(G1,G2)    - graph union assuming all nodes are different
    cartesian_product(G1,G2) - return Cartesian product graph
    compose(G1,G2)           - combine graphs identifying nodes common to both
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

