This is a guide for people moving from NetworkX 1.XX to NetworkX 2.0

As you know we have made some major changes to the methods in the Multi/Di/Graph classes.
Methods that used to return lists are removed and the methods that returned iterators
are renamed(removing the _iter suffix).
For example we hade two methods to get nodes of a graph, ``G.nodes()`` and ``G.nodes_iter()``. ``G.nodes_iter()`` is renamed to ``G.nodes()``, hence 
``G.nodes()`` returns an iterator now instead of list.

The methods changed are explained with examples below.

	>>> import networkx as nx
	>>> G = nx.complete_graph(5) 
	>>> G.nodes()
	<dictionary-keyiterator at 0x102ae8730>


People suprised by this output and expecting something like this

	>>> G.nodes()
	[0, 1, 2, 3, 4]

don't panic. Nothing is wrong.

Now ``G.nodes()`` returns an iterator. If you don't like this you can always get the old output by

	>>> list(G.nodes())
	[0, 1, 2, 3, 4]

In the same way for ``G.edges()``

	>>> G.edges()
	<generator object edges at 0x102ae9fa0>
	>>> list(G.edges())
	[(0, 1),
	 (0, 2),
	 (0, 3),
	 (0, 4),
	 (1, 2),
	 (1, 3),
	 (1, 4),
	 (2, 3),
	 (2, 4),
	 (3, 4)]

and ``G.neighbors(n)`` where n is a node.
 
	>>> G.neighbors(2)
	<dictionary-keyiterator at 0x102ae8aa0>

	>>> list(G.neighbors(2))
	[0, 1, 3, 4]

So, basically you can switch back to the old behavior by adding `list()` to the method.

BUT we did something different with ``G.degree()``. If a single node is passed as argument,
instead of returning an iterator or list, ``G.degree(n)`` now returns the degree of the node. Well this makes more sense.
``G.degree()`` follows the old practice (returning node, degree pairs) if more than one node is passed or nothing is passed.

	>>> G.degree(2)
	4
	>>> G.degree([1,2,3])
	<generator object d_iter at 0x102ba8780>
	>>> list(G.degree([1,2,3]))
	[(1, 4), (2, 4), (3, 4)]
	>>> dict(G.degree([1,2,3]))
	{1: 4, 2: 4, 3: 4}
	>>> G.degree()
	<generator object d_iter at 0x102ba8af0>
	>>> list(G.degree())
	[(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]
	>>> dict(G.degree())
	{0: 4, 1: 4, 2: 4, 3: 4, 4: 4}

``G.degree()`` used to return a dictionary. We can typecast the generator to return a list or dict as shown in the
above example.

Now lets move to DiGraphs. Everything is similar to Graphs. But we have a few more methods for DiGraphs.
Let's have a look on them.

	>>> D = nx.DiGraph()
	>>> D.add_edges_from([(1, 2), (2, 3), (1, 3), (2, 4)])
	>>> D.nodes()
	<dictionary-keyiterator at 0x102bd68e8>
	>>> list(D.nodes())
	[1, 2, 3, 4]
	>>> D.edges()
	<generator object edges at 0x102ba88c0>
	>>> list(D.edges())
	[(1, 2), (1, 3), (2, 3), (2, 4)] 
	>>> D.in_degree(2)
	1
	>>> D.out_degree(2)
	2
	>>> D.in_edges()
	<generator object in_edges at 0x102ba8cd0>
	>>> list(D.in_edges())
	[(1, 2), (1, 3), (2, 3), (2, 4)]
	>>> D.out_edges(2)
	<generator object edges at 0x102ba8c80>
	>>> list(D.out_edges(2))
	(2, 3), (2, 4)]
	>>> D.in_degree()
	<generator object d_iter at 0x102ba8a00>
	>>> list(D.in_degree())
	[(1, 0), (2, 1), (3, 2), (4, 1)]
	>>> D.successors(2)
	<dictionary-keyiterator at 0x102bdb418>
	>>> list(D.successors(2))
	[3, 4]
	>>> D.predecessors(2)
	<dictionary-keyiterator at 0x102bdb730>
	>>> list(D.predecessors(2))
	[1]

The same changes apply to MultiGraphs and MultiDiGraphs.

Any issues with these can be discussed on the [mailing list](https://groups.google.com/forum/#!forum/networkx-discuss)
