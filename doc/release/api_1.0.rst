*********************************
Version 1.0 notes and API changes
*********************************

We have made some significant API changes, detailed below, to add
functionality and clarity.  This page reflects changes from
networkx-0.99 to networkx-1.0.  For changes from earlier versions to
networkx-0.99 see :doc:`Version 0.99 API changes <api_0.99>`.

Version 1.0 requires Python 2.4 or greater.

Please send comments and questions to the networkx-discuss mailing list:
http://groups.google.com/group/networkx-discuss .


Version numbering
=================

In the future we will use a more standard release numbering system
with major.minor[build] labels where major and minor are numbers and
[build] is a label such as "dev1379" to indicate a development version
or "rc1" to indicate a release candidate.

We plan on sticking closer to a time-based release schedule with smaller
incremental changes released on a roughly quarterly basis.  The graph
classes API will remain fixed, unless we determine there are serious
bugs or other defects in the existing classes, until networkx-2.0 is
released at some time in the future.

Changes in base classes
=======================

The most significant changes in are in the graph classes.  All of the
graph classes now allow optional graph, node, and edge attributes.  Those
attributes are stored internally in the graph classes as dictionaries
and can be accessed simply like Python dictionaries in most cases.

Graph attributes
----------------
Each graph keeps a dictionary of key=value attributes
in the member G.graph.  These attributes can be accessed
directly using G.graph or added at instantiation using 
keyword arguments.

>>> G=nx.Graph(region='Africa')
>>> G.graph['color']='green'
>>> G.graph
{'color': 'green', 'region': 'Africa'}


Node attributes
---------------
Each node has a corresponding dictionary of attributes.
Adding attributes to nodes is optional.

Add node attributes using add_node(), add_nodes_from() or G.node

>>> G.add_node(1, time='5pm')
>>> G.add_nodes_from([3], time='2pm')
>>> G.node[1]
{'time': '5pm'}
>>> G.node[1]['room'] = 714
>>> G.nodes(data=True)
[(1, {'room': 714, 'time': '5pm'}), (3, {'time': '2pm'})]


Edge attributes
---------------
Each edge has a corresponding dictionary of attributes.
The default edge data is now an empty dictionary of attributes   
and adding attributes to edges is optional.

A common use case is to add a weight attribute to an edge:

>>> G.add_edge(1,2,weight=3.14159)

Add edge attributes using add_edge(), add_edges_from(), subscript
notation, or G.edge.

>>> G.add_edge(1, 2, weight=4.7 )
>>> G.add_edges_from([(3,4),(4,5)], color='red')
>>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])
>>> G[1][2]['weight'] = 4.7
>>> G.edge[1][2]['weight'] = 4



Methods changed
---------------

Graph(), DiGraph(), MultiGraph(), MultiDiGraph()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   Now takes optional keyword=value attributes on initialization.

   >>> G=nx.Graph(year='2009',city='New York')

add_node()
^^^^^^^^^^
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_node(1,room=714)


add_nodes_from()
^^^^^^^^^^^^^^^^	
   Now takes optional keyword=value attributes or a dictionary of 
   attributes applied to all affected nodes.

   >>> G.add_nodes_from([1,2],time='2pm')  # all nodes have same attribute 

add_edge()
^^^^^^^^^^
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_edge(1, 2, weight=4.7 )

add_edges_from()
^^^^^^^^^^^^^^^^	
   Now takes optional keyword=value attributes or a dictionary of 
   attributes applied to all affected edges.

   >>> G.add_edges_from([(3,4),(4,5)], color='red')
   >>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])


nodes() and nodes_iter()
^^^^^^^^^^^^^^^^^^^^^^^^
   New keyword data=True|False keyword determines whether to return
   two-tuples (n,dict) (True) with node attribution dictionary

   >>> G=nx.Graph([(1,2),(3,4)])
   >>> G.nodes(data=True)
   [(1, {}), (2, {}), (3, {}), (4, {})]

copy()
^^^^^^
   Now returns a deep copy of the graph (copies all underlying
   data and attributes for nodes and edges).  Use the class
   initializer to make a shallow copy:

   >>> G=nx.Graph()
   >>> G_shallow=nx.Graph(G) # shallow copy
   >>> G_deep=G.copy() # deep copy

to_directed(), to_undirected()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   Now returns a deep copy of the graph (copies all underlying
   data and attributes for nodes and edges).  Use the class
   initializer to make a shallow copy:

   >>> G=nx.Graph()
   >>> D_shallow=nx.DiGraph(G) # shallow copy
   >>> D_deep=G.to_directed() # deep copy

subgraph()
^^^^^^^^^^

   With copy=True now returns a deep copy of the graph 
   (copies all underlying data and attributes for nodes and edges).

   >>> G=nx.Graph()
   >>> # note: copy keyword deprecated in networkx>1.0
   >>> # H=G.subgraph([],copy=True) # deep copy of all data
   




add_cycle(), add_path(), add_star()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   Now take optional keyword=value attributes or a dictionary of 
   attributes which are applied to all edges affected by the method.

   >>> G=nx.Graph()
   >>> G.add_path([0,1,2,3],width=3.2)


Methods removed
---------------

delete_node()
^^^^^^^^^^^^^
   The preferred name is now remove_node().        


delete_nodes_from()
^^^^^^^^^^^^^^^^^^^
   No longer raises an exception on an attempt to delete a node not in
   the graph.  The preferred name is now remove_nodes_from().


delete_edge()
^^^^^^^^^^^^^
   Now raises an exception on an attempt to delete an edge not in the graph.
   The preferred name is now remove_edge().


delete_edges_from()
^^^^^^^^^^^^^^^^^^^
   The preferred name is now remove_edges_from().

has_neighbor():

   Use has_edge()  

get_edge()
^^^^^^^^^^
   Renamed to get_edge_data().	Returns the edge attribute dictionary.

   The fastest way to get edge data for edge (u,v) is to use G[u][v]
   instead of G.get_edge_data(u,v)


Members removed
---------------

directed, multigraph, weighted
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Use methods G.is_directed() and G.is_multigraph().
    All graphs are weighted graphs now if they have numeric
    values in the 'weight' edge attribute.


Methods added
-------------

add_weighted edges_from()
^^^^^^^^^^^^^^^^^^^^^^^^^ 
   Convenience method to add weighted edges to graph using a list of
   3-tuples (u,v,weight).

get_edge_data()
^^^^^^^^^^^^^^^
   Renamed from get_edge().	

   The fastest way to get edge data for edge (u,v) is to use G[u][v]
   instead of G.get_edge_data(u,v)

is_directed()
^^^^^^^^^^^^^
    replaces member G.directed

is_multigraph()
^^^^^^^^^^^^^^^
    replaces member G.multigraph



Classes Removed
---------------

LabeledGraph, LabeledDiGraph
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    These classes have been folded into the regular classes.

UbiGraph
^^^^^^^^
    Removed as the ubigraph platform is no longer being supported.


Additional functions/generators
===============================

ego_graph, stochastic_graph, PageRank algorithm, HITS algorithm, 
GraphML writer, freeze, is_frozen, A* algorithm, 
directed scale-free generator, random clustered graph.


Converting your existing code to networkx-1.0
=============================================

Weighted edges
--------------

Edge information is now stored in an attribution dictionary
so all edge data must be given a key to identify it.  

There is currently only one standard/reserved key, 'weight', which is
used by algorithms and functions that use weighted edges.  The
associated value should be numeric.  All other keys are available for
users to assign as needed.

>>> G=nx.Graph()
>>> G.add_edge(1,2,weight=3.1415) # add the edge 1-2 with a weight
>>> G[1][2]['weight']=2.3 # set the weight to 2.3

Similarly, for direct access the edge data, use 
the key of the edge data to retrieve it.

>>> w = G[1][2]['weight']

All NetworkX algorithms that require/use weighted edges now use the
'weight' edge attribute.  If you have existing algorithms that assumed
the edge data was numeric, you should replace G[u][v] and
G.get_edge(u,v) with G[u][v]['weight'].

An idiom for getting a weight for graphs with or without an assigned
weight key is

>>> w= G[1][2].get('weight',1)  # set w to 1 if there is no 'weight' key
