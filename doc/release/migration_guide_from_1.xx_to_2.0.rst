********************************
Migration guide from 1.XX to 2.0
********************************

This is a guide for people moving from NetworkX 1.XX to NetworkX 2.0

Any issues with these can be discussed on the `mailing list <https://groups.google.com/forum/#!forum/networkx-discuss>`_.

As you know we have made some major changes to the methods in the Multi/Di/Graph classes.
With the release of NetworkX 2.0 we are moving towards a view/iterator reporting API.
For example, ``G.nodes()`` now returns a NodeView (inspired from [dictionary views](https://docs.python.org/3/library/stdtypes.html#dict-views) in Python) and ``G.nodes_iter()`` has been removed.

The methods changed are explained with examples below.

	>>> import networkx as nx
	>>> G = nx.complete_graph(5) 
	>>> G.nodes()
	NodeView((0, 1, 2, 3, 4))

People suprised by this output and expecting something a list like this

	>>> G.nodes()
	[0, 1, 2, 3, 4]

don't panic, your code is not wrong.

Now ``G.nodes()`` returns an NodeView. You can iterate through ``G.nodes()`` just like a list.
	
	>>> for node in G.nodes():
	    ...:	print(node)
			0
			1
			2
			3
			4
	>>> list_of_nodes = [i for i in G.nodes()]
	>>> list_of_nodes
	[0, 1, 2, 3, 4]

By adding views NetworkX supports some cool new features like set operations on views.

	>>> H = nx.Graph()
	>>> H.add_nodes_from([1, 'networkx', '2.0'])
	>>> G.nodes() & H.nodes()  # finding common nodes in 2 graphs
	{1}
	>>> G.nodes() | H.nodes()  # union of nodes in 2 graphs 
	{0, 1, 2, 3, 4, '2.0', 'networkx'}

In the same way for ``G.edges()``

	>>> G.edges()
	EdgeView([(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])

``G.edges()`` return views instead of a list of edges and they also support set operations.

New feature include lookup of node and edge data from the views, property access without parentheses too.

	>>> G.add_node(3, color='blue')
	>>> G.nodes[3]
	'blue'
	>>> G.edge(0)
	EdgeDataView([(0, 1), (0, 2), (0, 3), (0, 4)])
	>>> G.edge[0, 1].update({'color': 'red'})
	>>> G.edge[0, 1]
	{'color': 'red'}

``G.degree()`` now returns a a dict like DegreeView

	>>> G.degree()
	DegreeView({0: 4, 1: 4, 2: 4, 3: 4, 4: 4})

Degree of an individual node can be calculated by ``G.degree(node)``. Same changes have been made to ``in_degree`` and ``out_degree`` for directed graphs.


``G.neighbors(n)`` where n is a node returns an iterator so we need .
 
	>>> G.neighbors(2)
	<dictionary-keyiterator at 0x102ae8aa0>

	>>> list(G.neighbors(2))
	[0, 1, 3, 4]


Now lets move to DiGraphs. Everything is similar to Graphs. But we have a few more methods for DiGraphs.
Let's have a look on them.

	>>> D = nx.DiGraph()
	>>> D.add_edges_from([(1, 2), (2, 3), (1, 3), (2, 4)])
	>>> D.nodes()
	NodeView((1, 2, 3, 4))
	>>> D.edges()
	OutEdgeView([(1, 2), (1, 3), (2, 3), (2, 4)])
	>>> D.in_degree(2)
	1
	>>> D.out_degree(2)
	2
	>>> D.in_edges()
	InEdgeView([(1, 2), (2, 3), (1, 3), (2, 4)])
	>>> D.out_edges(2)
	OutEdgeDataView([(2, 3), (2, 4)])
	>>> D.in_degree()
	InDegreeView({1: 0, 2: 1, 3: 2, 4: 1})
	>>> D.successors(2)
	<dictionary-keyiterator at 0x102bdb418>
	>>> list(D.successors(2))
	[3, 4]
	>>> D.predecessors(2)
	<dictionary-keyiterator at 0x102bdb730>
	>>> list(D.predecessors(2))
	[1]

The same changes apply to MultiGraphs and MultiDiGraphs.

The following methods have changed so if you have used these methods in your code it will be nice to revisit the code again and check everything is okay :)

* Graph/MultiGraph

  * ``G.nodes()``
  * ``G.edges()``
  * ``G.neighbors()``
  * ``G.adjacency_list()`` and ``G.adjacency_iter()`` to ``G.adjacency()``
  * ``G.degree()``
  * ``G.nodes_with_selfloops()``
  * ``G.selfloop_edges()``

* DiGraph/MultiDiGraph

  * ``G.nodes()``
  * ``G.edges()``
  * ``G.in_edges()``
  * ``G.out_edges()``
  * ``G.degree()``
  * ``G.in_degree()``
  * ``G.out_degree()``
