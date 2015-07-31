
Creating a graph
================

Create an empty graph with no nodes and no edges.

.. code:: python

    import networkx as nx

.. code:: python

    G = nx.Graph()

By definition, a :class:``Graph`` is a collection of nodes (vertices)
along with identified pairs of nodes (called edges, links, etc). In
NetworkX, nodes can be any hashable object e.g. a text string, an image,
an XML object, another Graph, a customized node object, etc. (Note:
Python's None object should not be used as a node as it determines
whether optional function arguments have been assigned in many
functions.)

Nodes
=====

The graph G can be grown in several ways. NetworkX includes many graph
generator functions and facilities to read and write graphs in many
formats. To get started though we'll look at simple manipulations. You
can add one node at a time,

.. code:: python

    G.add_node(1)

add a list of nodes,

.. code:: python

    G.add_nodes_from([2, 3])

or add any :term:``nbunch`` of nodes. An nbunch is any iterable
container of nodes that is not itself a node in the graph. (e.g. a list,
set, graph, file, etc..)

.. code:: python

    H = nx.path_graph(10)

.. code:: python

    G.add_nodes_from(H)

Note that G now contains the nodes of H as nodes of G. In contrast, you
could use the graph H as a node in G.

.. code:: python

    G.add_node(H)

The graph G now contains H as a node. This flexibility is very powerful
as it allows graphs of graphs, graphs of files, graphs of functions and
much more. It is worth thinking about how to structure your application
so that the nodes are useful entities. Of course you can always use a
unique identifier in G and have a separate dictionary keyed by
identifier to the node information if you prefer. (Note: You should not
change the node object if the hash depends on its contents.)

Edges
=====

G can also be grown by adding one edge at a time,

.. code:: python

    G.add_edge(1, 2)

.. code:: python

    e = (2, 3)

.. code:: python

    G.add_edge(*e) # unpack edge tuple*

by adding a list of edges,

.. code:: python

    G.add_edges_from([(1, 2),(1, 3)])

or by adding any :term:``ebunch`` of edges. An ebunch is any iterable
container of edge-tuples. An edge-tuple can be a 2-tuple of nodes or a
3-tuple with 2 nodes followed by an edge attribute dictionary, e.g.
(2,3,{'weight':3.1415}). Edge attributes are discussed further below

.. code:: python

    G.add_edges_from(H.edges())

One can demolish the graph in a similar fashion; using
:meth:``Graph.remove_node``, :meth:``Graph.remove_nodes_from``,
:meth:``Graph.remove_edge`` and :meth:``Graph.remove_edges_from``, e.g.

.. code:: python

    G.remove_node(H)

There are no complaints when adding existing nodes or edges. For
example, after removing all nodes and edges,

.. code:: python

    G.clear()

we add new nodes/edges and NetworkX quietly ignores any that are already
present.

.. code:: python

    G.add_edges_from([(1, 2), (1, 3)])

.. code:: python

    G.add_node(1)

.. code:: python

    G.add_edge(1, 2)

.. code:: python

    G.add_node("spam")       # adds node "spam"

.. code:: python

    G.add_nodes_from("spam") # adds 4 nodes: 's', 'p', 'a', 'm'

At this stage the graph G consists of 8 nodes and 2 edges, as can be
seen by:

.. code:: python

    G.number_of_nodes()




.. parsed-literal::

    8



.. code:: python

    G.number_of_edges()




.. parsed-literal::

    2



We can examine them with

.. code:: python

    list(G.nodes())  # G.nodes() returns an iterator of nodes.




.. parsed-literal::

    ['a', 1, 2, 3, 'spam', 'm', 'p', 's']



.. code:: python

    list(G.edges())  # G.edges() returns an iterator of edges.




.. parsed-literal::

    [(1, 2), (1, 3)]



.. code:: python

    list(G.neighbors(1))  # G.neighbors(n) returns an iterator of neigboring nodes of n




.. parsed-literal::

    [2, 3]



Removing nodes or edges has similar syntax to adding:

.. code:: python

    G.remove_nodes_from("spam")

.. code:: python

    list(G.nodes())




.. parsed-literal::

    [1, 2, 3, 'spam']



.. code:: python

    G.remove_edge(1, 3)

When creating a graph structure by instantiating one of the graph
classes you can specify data in several formats.

.. code:: python

    H = nx.DiGraph(G)  # create a DiGraph using the connections from G

.. code:: python

    list(H.edges())




.. parsed-literal::

    [(1, 2), (2, 1)]



.. code:: python

    edgelist = [(0, 1), (1, 2), (2, 3)]

.. code:: python

    H = nx.Graph(edgelist)

What to use as nodes and edges
==============================

You might notice that nodes and edges are not specified as NetworkX
objects. This leaves you free to use meaningful items as nodes and
edges. The most common choices are numbers or strings, but a node can be
any hashable object (except None), and an edge can be associated with
any object x using G.add\_edge(n1,n2,object=x).

As an example, n1 and n2 could be protein objects from the RCSB Protein
Data Bank, and x could refer to an XML record of publications detailing
experimental observations of their interaction.

We have found this power quite useful, but its abuse can lead to
unexpected surprises unless one is familiar with Python. If in doubt,
consider using :func:``convert_node_labels_to_integers`` to obtain a
more traditional graph with integer labels.

Accessing edges
===============

In addition to the methods :meth:``Graph.nodes``, :meth:``Graph.edges``,
and :meth:``Graph.neighbors``, iterator versions (e.g.
:meth:``Graph.edges_iter``) can save you from creating large lists when
you are just going to iterate through them anyway.

Fast direct access to the graph data structure is also possible using
subscript notation.

Warning

Do not change the returned dict--it is part of the graph data structure
and direct manipulation may leave the graph in an inconsistent state.

.. code:: python

    G[1]  # Warning: do not change the resulting dict




.. parsed-literal::

    {2: {}}



.. code:: python

    G[1][2]




.. parsed-literal::

    {}



You can safely set the attributes of an edge using subscript notation if
the edge already exists.

.. code:: python

    G.add_edge(1, 3)

.. code:: python

    G[1][3]['color']='blue'

Fast examination of all edges is achieved using adjacency(iterators).
Note that for undirected graphs this actually looks at each edge twice.

.. code:: python

    FG = nx.Graph()

.. code:: python

    FG.add_weighted_edges_from([(1, 2, 0.125), (1, 3, 0.75), (2 ,4 , 1.2), (3 ,4 , 0.375)])

.. code:: python

    for n,nbrs in FG.adjacency():
        for nbr,eattr in nbrs.items():
            data = eattr['weight']
            if data < 0.5:
                print('(%d, %d, %.3f)' % (n, nbr, data))


.. parsed-literal::

    (1, 2, 0.125)
    (2, 1, 0.125)
    (3, 4, 0.375)
    (4, 3, 0.375)


Convenient access to all edges is achieved with the edges method.

.. code:: python

    for (u, v, d) in FG.edges(data='weight'):
        if d < 0.5:
            print('(%d, %d, %.3f)'%(n, nbr, d))


.. parsed-literal::

    (4, 3, 0.125)
    (4, 3, 0.375)


Adding attributes to graphs, nodes, and edges
=============================================

Attributes such as weights, labels, colors, or whatever Python object
you like, can be attached to graphs, nodes, or edges.

Each graph, node, and edge can hold key/value attribute pairs in an
associated attribute dictionary (the keys must be hashable). By default
these are empty, but attributes can be added or changed using add\_edge,
add\_node or direct manipulation of the attribute dictionaries named
G.graph, G.node and G.edge for a graph G.

Graph attributes
================

Assign graph attributes when creating a new graph

.. code:: python

    G = nx.Graph(day="Friday")

.. code:: python

    G.graph




.. parsed-literal::

    {'day': 'Friday'}



Or you can modify attributes later

.. code:: python

    G.graph['day'] = 'Monday'

.. code:: python

    G.graph




.. parsed-literal::

    {'day': 'Monday'}



Node attributes
===============

Add node attributes using add\_node(), add\_nodes\_from() or G.node

.. code:: python

    G.add_node(1, time='5pm')

.. code:: python

    G.add_nodes_from([3], time='2pm')

.. code:: python

    G.node[1]




.. parsed-literal::

    {'time': '5pm'}



.. code:: python

    G.node[1]['room'] = 714

.. code:: python

    list(G.nodes(data=True))




.. parsed-literal::

    [(1, {'room': 714, 'time': '5pm'}), (3, {'time': '2pm'})]



Note that adding a node to G.node does not add it to the graph, use
G.add\_node() to add new nodes.

Edge attributes
===============

Add edge attributes using add\_edge(), add\_edges\_from(), subscript
notation, or G.edge.

.. code:: python

    G.add_edge(1, 2, weight=4.7)

.. code:: python

    G.add_edges_from([(3, 4), (4, 5)], color='red')

.. code:: python

    G.add_edges_from([(1, 2, {'color': 'blue'}), (2, 3, {'weight': 8})])

.. code:: python

    G[1][2]['weight'] = 4.7

.. code:: python

    G.edge[1][2]['weight'] = 4

.. code:: python

    list(G.edges(data=True))




.. parsed-literal::

    [(1, 2, {'color': 'blue', 'weight': 4}),
     (2, 3, {'weight': 8}),
     (3, 4, {'color': 'red'}),
     (4, 5, {'color': 'red'})]



The special attribute 'weight' should be numeric and holds values used
by algorithms requiring weighted edges.

Directed Graphs
===============

The :class:``DiGraph`` class provides additional methods specific to
directed edges, e.g. :meth:``DiGraph.out_edges``,
:meth:``DiGraph.in_degree``, :meth:``DiGraph.predecessors``,
:meth:``DiGraph.successors`` etc. To allow algorithms to work with both
classes easily, the directed versions of neighbors() and degree() are
equivalent to successors() and the sum of in\_degree() and out\_degree()
respectively even though that may feel inconsistent at times.

.. code:: python

    DG = nx.DiGraph()

.. code:: python

    DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])

.. code:: python

    DG.out_degree(1, weight='weight')




.. parsed-literal::

    0.5



.. code:: python

    DG.degree(1,weight='weight')




.. parsed-literal::

    1.25



.. code:: python

    list(DG.successors(1))   # DG.successors(n) returns an iterator




.. parsed-literal::

    [2]



.. code:: python

    list(DG.neighbors(1))   # DG.neighbors(n) returns an iterator




.. parsed-literal::

    [2]



Some algorithms work only for directed graphs and others are not well
defined for directed graphs. Indeed the tendency to lump directed and
undirected graphs together is dangerous. If you want to treat a directed
graph as undirected for some measurement you should probably convert it
using :meth:``Graph.to_undirected`` or with

.. code:: python

    H = nx.Graph(G) # convert G to undirected graph

MultiGraphs
===========

NetworkX provides classes for graphs which allow multiple edges between
any pair of nodes. The :class:``MultiGraph`` and :class:``MultiDiGraph``
classes allow you to add the same edge twice, possibly with different
edge data. This can be powerful for some applications, but many
algorithms are not well defined on such graphs. Shortest path is one
example. Where results are well defined, e.g.
:meth:``MultiGraph.degree`` we provide the function. Otherwise you
should convert to a standard graph in a way that makes the measurement
well defined.

.. code:: python

    MG = nx.MultiGraph()

.. code:: python

    MG.add_weighted_edges_from([(1, 2, .5), (1, 2, .75), (2, 3, .5)])

.. code:: python

    list(MG.degree(weight='weight'))  # MG.degree() returns a (node, degree) iterator




.. parsed-literal::

    [(1, 1.25), (2, 1.75), (3, 0.5)]



.. code:: python

    GG = nx.Graph()

.. code:: python

    for n,nbrs in MG.adjacency():
        for nbr,edict in nbrs.items():
            minvalue = min([d['weight'] for d in edict.values()])
            GG.add_edge(n,nbr, weight = minvalue)

.. code:: python

    nx.shortest_path(GG, 1, 3)




.. parsed-literal::

    [1, 2, 3]



Graph generators and graph operations
=====================================

In addition to constructing graphs node-by-node or edge-by-edge, they
can also be generated by

-  Applying classic graph operations, such as:

   ::

       subgraph(G, nbunch)      - induce subgraph of G on nodes in nbunch
       union(G1,G2)             - graph union
       disjoint_union(G1,G2)    - graph union assuming all nodes are different
       cartesian_product(G1,G2) - return Cartesian product graph
       compose(G1,G2)           - combine graphs identifying nodes common to both
       complement(G)            - graph complement
       create_empty_copy(G)     - return an empty copy of the same graph class
       convert_to_undirected(G) - return an undirected representation of G
       convert_to_directed(G)   - return a directed representation of G

-  Using a call to one of the classic small graphs, e.g.

.. code:: python

    petersen = nx.petersen_graph()

.. code:: python

    tutte = nx.tutte_graph()

.. code:: python

    maze = nx.sedgewick_maze_graph()

.. code:: python

    tet = nx.tetrahedral_graph()

-  Using a (constructive) generator for a classic graph, e.g.

.. code:: python

    K_5 = nx.complete_graph(5)

.. code:: python

    K_3_5 = nx.complete_bipartite_graph(3, 5)

.. code:: python

    barbell = nx.barbell_graph(10, 10)

.. code:: python

    lollipop = nx.lollipop_graph(10, 20)

-  Using a stochastic graph generator, e.g.

.. code:: python

    er = nx.erdos_renyi_graph(100, 0.15)

.. code:: python

    ws = nx.watts_strogatz_graph(30, 3, 0.1)

.. code:: python

    ba = nx.barabasi_albert_graph(100, 5)

.. code:: python

    red = nx.random_lobster(100, 0.9, 0.9)

-  Reading a graph stored in a file using common graph formats, such as
   edge lists, adjacency lists, GML, GraphML, pickle, LEDA and others.

.. code:: python

    nx.write_gml(red, "path.to.file")

.. code:: python

    mygraph = nx.read_gml("path.to.file")

Details on graph formats: :doc:``/reference/readwrite``

Details on graph generator functions: :doc:``/reference/generators``

Analyzing graphs
================

The structure of G can be analyzed using various graph-theoretic
functions such as:

.. code:: python

    G=nx.Graph()

.. code:: python

    G.add_edges_from([(1, 2), (1, 3)])

.. code:: python

    G.add_node("spam")       # adds node "spam"

.. code:: python

    nx.connected_components(G)




.. parsed-literal::

    <generator object connected_components at 0x103ed7cd0>



.. code:: python

    list(nx.connected_components(G))




.. parsed-literal::

    [{1, 2, 3}, {'spam'}]



.. code:: python

    sorted(d for n, d in nx.degree(G))




.. parsed-literal::

    [0, 1, 1, 2]



.. code:: python

    nx.clustering(G)




.. parsed-literal::

    {1: 0.0, 2: 0.0, 3: 0.0, 'spam': 0.0}



Functions that return node properties return (node, value) tuple
iterators.

.. code:: python

    nx.degree(G)




.. parsed-literal::

    <generator object d_iter at 0x103ed7d20>



.. code:: python

    list(nx.degree(G))




.. parsed-literal::

    [(1, 2), (2, 1), (3, 1), ('spam', 0)]



For values of specific nodes, you can provide a single node or an nbunch
of nodes as argument. If a single node is specified, then a single value
is returned. If an nbunch is specified, then the function will return a
(node, degree) iterator.

.. code:: python

    nx.degree(G, 1)




.. parsed-literal::

    2



.. code:: python

    G.degree(1)




.. parsed-literal::

    2



.. code:: python

    G.degree([1, 2])




.. parsed-literal::

    <generator object d_iter at 0x103ef00a0>



.. code:: python

    list(G.degree([1, 2]))




.. parsed-literal::

    [(1, 2), (2, 1)]



Details on graph algorithms supported: :doc:``/reference/algorithms``

Drawing graphs
==============

NetworkX is not primarily a graph drawing package but basic drawing with
Matplotlib as well as an interface to use the open source Graphviz
software package are included. These are part of the networkx.drawing
package and will be imported if possible. See
:doc:``/reference/drawing`` for details.

Note that the drawing package in NetworkX is not yet compatible with
Python versions 3.0 and above.

First import Matplotlib's plot interface (pylab works too)

.. code:: python

    import matplotlib.pyplot as plt

You may find it useful to interactively test code using "ipython
-pylab", which combines the power of ipython and matplotlib and provides
a convenient interactive mode.

To test if the import of networkx.drawing was successful draw G using
one of

.. code:: python

    nx.draw(G)

.. code:: python

    nx.draw_random(G)

.. code:: python

    nx.draw_circular(G)

.. code:: python

    nx.draw_spectral(G)

when drawing to an interactive display. Note that you may need to issue
a Matplotlib

.. code:: python

    plt.show()

command if you are not using matplotlib in interactive mode: (See
Matplotlib FAQ )

To save drawings to a file, use, for example

.. code:: python

    nx.draw(G)

.. code:: python

    plt.savefig("path.png")

writes to the file "path.png" in the local directory.

Details on drawing graphs: :doc:``/reference/drawing``
