*******************************
Migration guide from 1.X to 2.0
*******************************

This is a guide for people moving from NetworkX 1.X to NetworkX 2.0

Any issues with these can be discussed on the `mailing list <https://groups.google.com/forum/#!forum/networkx-discuss>`_.

We have made some major changes to the methods in the Multi/Di/Graph classes.
The methods changed are explained with examples below.

With the release of NetworkX 2.0 we are moving to a view/iterator reporting API.
Methods that used to return containers now return views (inspired from
[dictionary views](https://docs.python.org/3/library/stdtypes.html#dict-views)
in Python) and methods that returned iterators have been removed.
For example, ``G.nodes`` (or ``G.nodes()``)  now returns a NodeView and
``G.nodes_iter()`` has been removed.

    >>> import networkx as nx
    >>> G = nx.complete_graph(5)
    >>> G.nodes  # for backward compatibility G.nodes() works as well
    NodeView((0, 1, 2, 3, 4))

If you want a list of nodes use the Python list function

    >>> list(G.nodes)
    [0, 1, 2, 3, 4]


You can also iterate through ``G.nodes`` (or ``G.nodes()``)

    >>> for node in G.nodes:
    ...     print(node)
    0
    1
    2
    3
    4

By adding views NetworkX supports some new features like set operations on
views.

    >>> H = nx.Graph()
    >>> H.add_nodes_from([1, 'networkx', '2.0'])
    >>> G.nodes & H.nodes  # finding common nodes in 2 graphs
    set([1])
    >>> G.nodes | H.nodes  # union of nodes in 2 graphs
    set([0, 1, 2, 3, 4, 'networkx', '2.0'])

Similarly, ``G.edges`` now returns an EdgeView instead of a list of edges and it
also supports set operations.

    >>> G.edges  # for backward compatibility G.nodes() works as well
    EdgeView([(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)])
    >>> list(G.edges)
    [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]

``G.degree`` now returns a ``dict``-like DegreeView

    >>> G.degree  # for backward compatibility G.degree() works as well
    DegreeView({0: 4, 1: 4, 2: 4, 3: 4, 4: 4})
    >>> G.degree([1, 2, 3])
    DegreeView({1: 4, 2: 4, 3: 4})
    >>> list(G.degree([1, 2, 3]))
    [(1, 4), (2, 4), (3, 4)]
    >>> dict(G.degree([1, 2, 3]))
    {1: 4, 2: 4, 3: 4}
    >>> G.degree
    DegreeView({0: 4, 1: 4, 2: 4, 3: 4, 4: 4})
    >>> list(G.degree)
    [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]
    >>> dict(G.degree)
    {0: 4, 1: 4, 2: 4, 3: 4, 4: 4}

The degree of an individual node can be calculated by ``G.degree[node]``.
Similar changes have been made to ``in_degree`` and ``out_degree``
for directed graphs.

If ``n`` is a node in ``G``, then ``G.neighbors(n)`` returns an iterator.

    >>> G.neighbors(2)
    <dictionary-keyiterator object at ...>
    >>> list(G.neighbors(2))
    [0, 1, 3, 4]

DiGraphs behave similar to Graphs, but have a few more methods.

    >>> D = nx.DiGraph()
    >>> D.add_edges_from([(1, 2), (2, 3), (1, 3), (2, 4)])
    >>> D.nodes
    NodeView((1, 2, 3, 4))
    >>> list(D.nodes)
    [1, 2, 3, 4]
    >>> D.edges
    OutEdgeView([(1, 2), (1, 3), (2, 3), (2, 4)])
    >>> list(D.edges)
    [(1, 2), (1, 3), (2, 3), (2, 4)]
    >>> D.in_degree[2]
    1
    >>> D.out_degree[2]
    2
    >>> D.in_edges
    InEdgeView([(1, 2), (1, 3), (2, 3), (2, 4)])
    >>> list(D.in_edges())
    [(1, 2), (1, 3), (2, 3), (2, 4)]
    >>> D.out_edges(2)
    OutEdgeDataView([(2, 3), (2, 4)])
    >>> list(D.out_edges(2))
    [(2, 3), (2, 4)]
    >>> D.in_degree
    InDegreeView({1: 0, 2: 1, 3: 2, 4: 1})
    >>> list(D.in_degree)
    [(1, 0), (2, 1), (3, 2), (4, 1)]
    >>> D.successors(2)
    <dictionary-keyiterator object at ...>
    >>> list(D.successors(2))
    [3, 4]
    >>> D.predecessors(2)
    <dictionary-keyiterator object at ...>
    >>> list(D.predecessors(2))
    [1]

The same changes apply to MultiGraphs and MultiDiGraphs.
 
-------

The order of arguments to ``set_edge_attributes`` and ``set_node_attributes`` has
changed.  The position of ``name`` and ``values`` has been swapped, and ``name`` now
defaults to ``None``.  The previous call signature of ``(graph, name, value)`` has
been changed to ``(graph, value, name=None)``. The new style allows for ``name`` to
be omitted in favor of passing a dictionary of dictionaries to ``values``.

A simple method for migrating existing code to the new version is to explicitly
specify the keyword argument names. This method is backwards compatible and
ensures the correct arguments are passed, regardless of the order. For example the old code

    >>> G = nx.Graph([(1, 2), (1, 3)])
    >>> nx.set_node_attributes(G, 'label', {1: 'one', 2: 'two', 3: 'three'})  # doctest: +SKIP
    >>> nx.set_edge_attributes(G, 'label', {(1, 2): 'path1', (2, 3): 'path2'})  # doctest: +SKIP

Will cause ``TypeError: unhashable type: 'dict'`` in the new version. The code
can be refactored as

    >>> G = nx.Graph([(1, 2), (1, 3)])
    >>> nx.set_node_attributes(G, name='label', values={1: 'one', 2: 'two', 3: 'three'})
    >>> nx.set_edge_attributes(G, name='label', values={(1, 2): 'path1', (2, 3): 'path2'})
