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

   >>> G=Graph(year='2009',city='New York')

add_node()
^^^^^^^^^^
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_node(1,room=714)


add_nodes_from()
^^^^^^^^^^^^^^^^	
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_nodes_from([1,2],time='2pm')  # all nodes have same attribute 

add_edge()
^^^^^^^^^^
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_edge(1, 2, weight=4.7 )

add_edges_from()
^^^^^^^^^^^^^^^^	
   Now takes optional keyword=value attributes or a dictionary of attributes.

   >>> G.add_edges_from([(3,4),(4,5)], color='red')
   >>> G.add_edges_from([(1,2,{'color':'blue'}), (2,3,{'weight':8})])


nodes() and nodes_iter()
^^^^^^^^^^^^^^^^^^^^^^^^
   New keyword data=True|False keyword determines whether to return
   two-tuples (n,dict) (True) with node attribution dictionary

   >>> G=Graph([(1,2),(3,4)]
   >>> G.nodes(data=True)
   [(1, {}), (2, {}), (3, {}), (4, {})]

copy()
^^^^^^
   Now returns a deep copy of the graph (copies all underlying
   data and attributes for nodes and edges).  Use the class
   initializer to make a shallow copy:

   >>> G=Graph()
   >>> G_shallow=Graph(G) # shallow copy
   >>> G_deep=G.copy() # deep copy

to_directed(), to_undirected()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   Now returns a deep copy of the graph (copies all underlying
   data and attributes for nodes and edges).  Use the class
   initializer to make a shallow copy:

   >>> G=Graph()
   >>> D_shallow=DiGraph(G) # shallow copy
   >>> D_deep=G.to_directed() # deep copy

subgraph()
^^^^^^^^^^

   With copy=True now returns a deep copy of the graph 
   (copies all underlying data and attributes for nodes and edges).

   >>> G=Graph()
   >>> H=G.subgraph(copy=True) # deep copy of all data



add_cycle(), add_path(), add_star()
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   Now take optional keyword=value attributes or a dictionary of attributes.

   >>> G=Graph()
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
^^^^^^^^^^^^^^
   Now raises an exception on an attempt to delete an edge not in the graph.
   The preferred name is now remove_edge().


delete_edges_from()
^^^^^^^^^^^^^^^^^^^
   The preferred name is now remove_edges_from().

has_neighbor():

   Use has_edge()  

get_edge()
^^^^^^^^^^
   Renamed to get_edge_data().	

   The fastest way to get edge data for edge (u,v) is to use G[u][v]
   instead of G.get_edge_data(u,v)


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



Other possible incompatibilities with existing code
===================================================


Converting your existing code to networkx-1.0
=============================================


