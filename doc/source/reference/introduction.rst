Introduction
~~~~~~~~~~~~
NetworkX provides data structures for graphs (or networks)
along with graph algorithms, generators, and drawing tools.

History and goals
=================
NetworkX is intended to:

-  Be a tool to study the structure and
   dynamics of social, biological, and infrastructure networks

-  Provide ease-of-use and rapid
   development in a collaborative, multidisciplinary environment 

-  Be an Open-source software package that can provide functionality
   to a diverse community of active and easily participating users
   and developers. 

-  Provide an easy interface to 
   existing code bases written in C, C++, and FORTRAN 

-  Painlessly slurp in large nonstandard data sets 

-  Provide a standard API and/or graph implementation that is 
   suitable for many applications. 

History:

-  NetworkX was inspired by Guido van Rossum's 1998 Python 
   graph representation essay:ref:`[1]<references>`. 

-  First public release in April 2005.  Version 1.0 released in 2009.


Overview
========
The structure of NetworkX can be seen by the organization of its source code.
The package provides classes for graph objects, generators to create standard
graphs, IO routines for reading in existing datasets, algorithms to analyse
the resulting networks and some basic drawing tools.

Most of the NetworkX API is provided by functions which take a graph object
as an argument.  Methods of the graph object are limited to basic manipulation
and reporting.  This provides modularity of code and documentation. 
It also makes it easier for newcomers to learn about the package in stages.  
The source code for each module is meant to be easy to read and reading 
this Python code is actually a good way to learn more about network algorithms, 
but we have put a lot of effort into making the documentation sufficient and friendly. 
If you have suggestions or questions please contact us by joining the 
`NetworkX Google group <http://groups.google.com/group/networkx-discuss>`_.

Classes are named using CamelCase (capital letters at the start of each word).
functions, methods and variable names are lower_case_underscore (lowercase with
an underscore representing a space between words).

Graphs
=======
The first choice to be made when using NetworkX is what type of graph object to use.
A graph (network) is a collection of nodes together with a collection of edges
that are pairs of nodes.  Attributes are often associated with nodes and/or edges.
Our graph objects come in different flavors depending on two main properties of
the network:

 - directed:  Are the edges **directed**?  Does the order of the edge pairs (u,v) matter?
   A directed graph is specified by the "Di" prefix in the class name, e.g. DiGraph().
   We make this distinction because many classical graph properties are defined 
   differently for directed graphs.

 - multiedges:  Are multiple edges allowed between each pair of nodes?  
   As you might imagine, multiple edges requires a different data structure, 
   though tricky users could design edge data objects to support this functionality.  
   We provide a standard data structure and interface for this type of graph 
   using the prefix "Multi", e.g. MultiGraph().

The basic graph classes are named:  
:doc:`Graph </reference/classes.graph>`, :doc:`DiGraph</reference/classes.digraph>`, 
:doc:`MultiGraph </reference/classes.multigraph>`, and 
:doc:`MultiDiGraph </reference/classes.multidigraph>`

A third graph attribute (**weighted**) signifies whether the edge data is numeric.
Some algorithms depend on numeric edge data.  By default this attribute is True,
but if you use more complicated edge data you may want to set it to False so that
any algorithms that using numeric edge data can warn you if you try to use them.


Nodes and Edges
---------------
The next choice you have to make when specifying a graph is what kinds of nodes
and edges to use.  If the topology of the network is all you care about then
using integers or strings as the nodes makes sense and you need not worry about
edge data.  If you have a data structure already in place to describe nodes you
can simply use that structure as your nodes provided it is hashable.  If it is
not hashable you can use a unique identifier to represent the node.

Edges often have data associated with them.  If the data is numeric, the graph 
is **weighted**.  Some of the graph algorithms, such as Dijkstra's shortest path
algorithm, will not work unless the edge data is a number.  In other cases
more than one attribute is associated with an edge.  Here you have to make a
choice based on how you plan to use your data.  If you will mostly examine
each attribute over the entire graph, it may be best to create more than one
graph object--each corresponding to a given attribute.  If you will be traversing
the edges of the network and looking at more than one attribute of each edge, then
it may make more sense to create a single graph object with more complicated data
representing each edge.  Edge data is arbitrary in NetworkX so you can make it  
anything from a tuple to a customized object for your application.  


Once you've decided how to encode the nodes and edges, and whether you have
an undirected/directed graph with or without multiedges you are ready to build 
your network.

Graph Creation
==============
NetworkX graph objects can be created in one of three ways:

 - Graph generators -- standard algorithms to create network topologies.
 - Importing data from pre-existing (usually file) sources.
 - Adding edges and nodes explicitly.

Manual addition and removing of nodes/edges is the easiest to describe.
Each graph object supplies methods to manipulate the graph.  For example,

>>> import networkx as nx
>>> G=nx.Graph()
>>> G.add_edge(1,2)      # default edge data=1
>>> G.add_edge(2,3,weight=0.9)  # you can specify edge data
>>> import math
>>> G.add_edge('y','x',function=math.cos) # edge attributes can be anything
>>> G.add_node(math.cos) # any hashable can be a node

>>> elist=[('a','b',0.3),('b','c',0.9),('a','c',0.5),('c','d',1.2)]
>>> G.add_weighted_edges_from(elist)  # add multiple edges at once

You can see the :doc:`/tutorial/index` for more examples.
Some basic graph operations such as union and intersection
are described in the :ref:`operators module<operators>` documentation.

Graph generators such as binomial_graph and powerlaw_graph are provided in the
:doc:`generators` subpackage.

For importing network data from formats such as GML, GraphML, edge list text files
see the :doc:`readwrite` subpackage.


Graph Reporting
===============
Class methods are used for the basic reporting functions neighbors, edges and degree.
Reporting of lists is often needed only to iterate through that list so we supply
iterator versions of many property reporting methods.  For example edges() and 
nodes() have corresponding methods edges_iter() and nodes_iter().  
Using these methods when you can will save memory and often time as well.

The basic graph relationship of an edge can be obtained in two basic ways.
One can look for neighbors of a node or one can look for edges incident to
a node.  We jokingly refer to people who focus on nodes/neighbors as node-centric
and people who focus on edges as edge-centric.  The designers of NetworkX
tend to be node-centric and view edges as a relationship between nodes.  
You can see this by our avoidance of notation like G[u,v] in favor of G[u][v].
Most data structures for sparse graphs are essentially adjacency lists and so
fit this perspective.  In the end, of course, it doesn't really matter which way
you examine the graph.  G.edges() removes duplicate representations of each edge
while G.neighbors(n) or G[n] is slightly faster but doesn't remove duplicates.

Any properties that are more complicated than edges, neighbors and degree are
provided by functions.  For example nx.triangles(G,n) gives the number of triangles
which include node n as a vertex.  These functions are grouped in the code and 
documentation under the term :ref:`algorithms<algorithms>`.


Algorithms
==========
A number of graph algorithms are provided with NetworkX.
These include shortest path, and breadth first search (see Traversal)
clustering and isomorphism algorithms and others.  There are
many that we have not developed yet too.  If you implement a
graph algorithm that might be useful for others please let 
us know through the Google group or the developer website.

As an example here is code to use Dijkstra's algorithm to 
find the shortest weighted path: 

>>> G=nx.Graph()
>>> e=[('a','b',0.3),('b','c',0.9),('a','c',0.5),('c','d',1.2)]
>>> G.add_weighted_edges_from(e)
>>> print nx.dijkstra_path(G,'a','d')
['a', 'c', 'd']

Drawing
=======
While NetworkX is not designed as a network layout tool, we provide
a simple interface to drawing packages and some simple layout algorithms. 
We interface to the excellent Graphviz layout tools like dot and neato
with the (suggested) pygraphviz package or the pydot interface.
Drawing can be done using external programs or the Matplotlib Python
package.  Interactive GUI interfaces are possible though not provided.
The drawing tools are provided in the module :ref:`drawing<drawing>`.

The basic drawing functions essentially place the nodes on a scatterplot
using the positions in a dict or computed with a layout function.  The
edges are then lines between those dots.  

>>> G=nx.cubical_graph()
>>> nx.draw(G)   # default spring_layout
>>> nx.draw(G,pos=nx.spectral_layout(G),nodecolor='r',edge_color='b')

See the examples for more ideas.

Data Structure
==============
NetworkX uses a "dictionary of dictionaries of dictionaries" as the basic network 
data structure.  This allows fast lookup with reasonable storage for large sparse 
networks.  The keys are nodes so G[u] returns an adjacency dict keyed by neighbor 
to the edge attribute dict.   The expression G[u][v] returns the edge attribute
dictionary itself.  A dictionary of lists would have also been possible, but 
not allowed fast edge detection nor convenient storage of edge data.

Advantages of dict-of-dicts-of-dicts data structure
  
 - Find edges and remove edges with two dictionary look-ups 
 - Prefer to "lists" because of fast lookup with sparse storage.
 - Prefer to "sets" since data can be attached to edge
 - G[u][v] returns the edge attribute dictionary
 - ``n in G`` tests if node ``n`` is in graph G
 - ``for n in G:`` iterates through the graph.
 - ``for nbr in G[n]:`` iterates through neighbors.

As an example, here is a representation of an undirected graph with the 
edges $A-B$, $B-C$

>>> G=nx.Graph()
>>> G.add_edge('A','B')
>>> G.add_edge('B','C')
>>> print G.adj
{'A': {'B': {}}, 
 'B': {'A': {}, 'C': {}}, 
 'C': {'B': {}}}

The data structure gets morphed slightly for each base graph class.
For DiGraph two dict-of-dicts-of-dicts structures are provided, one 
for successors and one for predecessors.
For MultiGraph/MultiDiGraph we use a dict-of-dicts-of-dicts-of-dicts 
where the third dict is keyed by an edge key identifier to the fourth 
dict which contains the edge attributes for that edge between the two nodes.

Graphs use a dictionary of attributes for each edge.
We use a dict-of-dicts-of-dicts data structure with the inner 
dict storing "name-value" relationships for that edge.

>>> G=nx.Graph()
>>> G.add_edge(1,2,color='red',weight=0.84,size=300)
>>> print G[1][2]['size']
300

The dict-of-dicts data structure is based on the following

References
----------

.. _references:

Guido van Rossum.
Python Patterns - Implementing Graphs, 1998.
http://www.python.org/doc/essays/graphs/

David Eppstein.
{PADS}, a library of {P}ython {A}lgorithms and {D}ata {S}tructures,
2008.

