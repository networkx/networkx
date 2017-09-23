************************
Version 0.99 API changes
************************

The version networkx-0.99 is the penultimate release before
networkx-1.0.  We have bumped the version from 0.37 to 0.99 to
indicate (in our unusual version number scheme) that this is a major
change to NetworkX.  

We have made some significant changes, detailed below, to NetworkX
to improve  performance, functionality, and clarity. 

Version 0.99 requires Python 2.4 or greater.

Please send comments and questions to the networkx-discuss mailing list.
http://groups.google.com/group/networkx-discuss

Changes in base classes
=======================

The most significant changes are in the graph classes. 
We have redesigned the Graph() and DiGraph() classes 
to optionally allow edge data.
This change allows Graph and DiGraph to naturally represent
weighted graphs and to hold arbitrary information on edges.

 - Both Graph and DiGraph take an optional argument weighted=True|False.
   When weighted=True the graph is assumed to have numeric edge data
   (with default 1).  The Graph and DiGraph classes in earlier versions
   used the Python None as data (which is still allowed as edge data).

 - The Graph and DiGraph classes now allow self loops.

 - The XGraph and XDiGraph classes are removed and replaced with 
   MultiGraph and MultiDiGraph. MultiGraph and MultiDiGraph
   optionally allow parallel (multiple) edges between two nodes.

The mapping from old to new classes is as follows::

 - Graph -> Graph (self loops allowed now, default edge data is 1)
 - DiGraph -> DiGraph (self loops allowed now, default edge data is 1)
 - XGraph(multiedges=False) -> Graph
 - XGraph(multiedges=True) -> MultiGraph
 - XDiGraph(multiedges=False) -> DiGraph
 - XDiGraph(multiedges=True) -> MultiDiGraph


Methods changed
---------------

edges()
^^^^^^^
   New keyword data=True|False keyword determines whether to return
   two-tuples (u,v) (False) or three-tuples (u,v,d) (True)


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


add_edge()
^^^^^^^^^^
   The add_edge() method no longer accepts an edge tuple (u,v)
   directly.  The tuple must be unpacked into individual nodes. 

   >>> import networkx as nx
   >>> u='a'
   >>> v='b'
   >>> e=(u,v)
   >>> G=nx.Graph()
   
   Old

   >>> # G.add_edge((u,v))  # or G.add_edge(e) 

   New 

   >>> G.add_edge(*e) # or G.add_edge(*(u,v)) 

   The * operator unpacks the edge tuple in the argument list.

   Add edge now has
   a data keyword parameter for setting the default (data=1) edge
   data.
   
   >>> # G.add_edge('a','b','foo')  # add edge with string "foo" as data
   >>> # G.add_edge(1,2,5.0)  # add edge with float 5 as data
   


add_edges_from()
^^^^^^^^^^^^^^^^
   Now can take list or iterator of either 2-tuples (u,v),
   3-tuples (u,v,data) or a mix of both.  

   Now has data keyword parameter (default 1) for setting the edge data
   for any edge in the edge list that is a 2-tuple.


has_edge()
^^^^^^^^^^
   The has_edge() method no longer accepts an edge tuple (u,v)
   directly.  The tuple must be unpacked into individual nodes. 

   Old: 

   >>> # G.has_edge((u,v))  # or has_edge(e)

   New: 

   >>> G.has_edge(*e) # or has_edge(*(u,v)) 
   True
   
   The * operator unpacks the edge tuple in the argument list.

get_edge()
^^^^^^^^^^
   Now has the keyword argument "default" to specify
   what value to return if no edge is found.  If not specified
   an exception is raised if no edge is found.
   
   The fastest way to get edge data for edge (u,v) is to use G[u][v]
   instead of G.get_edge(u,v)


degree_iter()
^^^^^^^^^^^^^
   The degree_iter method now returns an iterator over pairs of (node,
   degree).  This was the previous behavior of degree_iter(with_labels=true)    
   Also there is a new keyword weighted=False|True for weighted degree.

subgraph()
^^^^^^^^^^
   The argument inplace=False|True has been replaced with copy=True|False.     

   Subgraph no longer takes create_using keyword.  To change the graph
   type either make a copy of
   the graph first and then change type or change type and make
   a subgraph.  E.g.

   >>> G=nx.path_graph(5)
   >>> H=nx.DiGraph(G.subgraph([0,1])) # digraph of copy of induced subgraph

__getitem__()
^^^^^^^^^^^^^
   Getting node neighbors from the graph with G[v] now returns
   a dictionary.

   >>> G=nx.path_graph(5)
   >>> # G[0]
   #  {1: 1}

   To get a list of neighbors you can either use the keys of that
   dictionary or use

   >>> G.neighbors(0)  # doctest: +SKIP
   [1]
   
   This change allows algorithms to use the underlying dict-of-dict
   representation through G[v] for substantial performance gains.  
   Warning: The returned dictionary should not be modified as it may
   corrupt the graph data structure.  Make a copy G[v].copy() if you 
   wish to modify the dict.


Methods removed
---------------

info()
^^^^^^
   now a function

   >>> G=nx.Graph(name='test me')
   >>> nx.info(G)  # doctest: +SKIP
   Name:                  test me
   Type:                  Graph
   Number of nodes:       0
   Number of edges:       0


node_boundary()
^^^^^^^^^^^^^^^
   now a function

edge_boundary() 
^^^^^^^^^^^^^^^ 
   now a function

is_directed() 
^^^^^^^^^^^^^
   use the directed attribute 

   >>> G=nx.DiGraph()
   >>> # G.directed
   #  True

G.out_edges()
^^^^^^^^^^^^^
   use G.edges()

G.in_edges() 
^^^^^^^^^^^^ 
   use

   >>> G = nx.DiGraph()
   >>> R = G.reverse()
   >>> R.edges()  # doctest: +SKIP
   []

   or

   >>> [(v,u) for (u,v) in G.edges()]
   []

Methods added
-------------

adjacency_list()
^^^^^^^^^^^^^^^^
Returns a list-of-lists adjacency list representation of the graph.

adjacency_iter()
^^^^^^^^^^^^^^^^
Returns an iterator of (node, adjacency_dict[node]) over all
nodes in the graph.  Intended for fast access to the internal
data structure for use in internal algorithms.


Other possible incompatibilities with existing code
===================================================

Imports
-------
Some of the code modules were moved into subdirectories.

Import statements such as:: 

  import networkx.centrality
  from networkx.centrality import *

may no longer work (including that example). 

Use either

>>> import networkx # e.g. centrality functions available as networkx.fcn()

or

>>> from networkx import * # e.g. centrality functions available as fcn()

Self-loops
----------
For Graph and DiGraph self loops are now allowed.
This might affect code or algorithms that add self loops 
which were intended to be ignored.

Use the methods

   - nodes_with_selfloops()
   - selfloop_edges()
   - number_of_selfloops()

to discover any self loops.

Copy
----
Copies of NetworkX graphs including using the copy() method
now return complete copies of the graph.  This means that all
connection information is copied--subsequent changes in the
copy do not change the old graph.  But node keys and edge 
data in the original and copy graphs are pointers to the same data.

prepare_nbunch
--------------
Used internally - now called nbunch_iter and returns an iterator.


Converting your old code to Version 0.99
========================================

Mostly you can just run the code and python will raise an exception 
for features that changed.  Common places for changes are

    - Converting XGraph() to either Graph or MultiGraph
    - Converting XGraph.edges()  to  Graph.edges(data=True)
    - Switching some rarely used methods to attributes (e.g. directed)
      or to functions (e.g. node_boundary)
    - If you relied on the old default edge data being None, you will 
      have to account for it now being 1.

You may also want to look through your code for places which could 
improve speed or readability.  The iterators are helpful with large
graphs and getting edge data via G[u][v] is quite fast.   You may also
want to change G.neighbors(n) to G[n] which returns the dict keyed by 
neighbor nodes to the edge data.  It is faster for many purposes but
does not work well when you are changing the graph.

