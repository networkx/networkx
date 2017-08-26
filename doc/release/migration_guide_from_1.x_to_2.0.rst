*******************************
Migration guide from 1.X to 2.0
*******************************

This is a guide for people moving from NetworkX 1.X to NetworkX 2.0

Any issues with these can be discussed on the `mailing list
<https://groups.google.com/forum/#!forum/networkx-discuss>`_.

At the bottom of this document we discuss how to create code that will
work with both NetworkX v1.x and v2.0.

We have made some major changes to the methods in the Multi/Di/Graph classes.
The methods changed are explained with examples below.

With the release of NetworkX 2.0 we are moving to a view/iterator reporting API.
We have moved many methods from reporting lists or dicts to iterating over
the information. Most of the changes in this regard are in the base classes.
Methods that used to return containers now return views (inspired from
`dictionary views <https://docs.python.org/3/library/stdtypes.html#dict-views>`_
in Python) and methods that returned iterators have been removed.
The methods which create new graphs have changed in the depth of data copying.
``G.subgraph``/``edge_subgraph``/``reverse``/``to_directed``/``to_undirected``
are affected.  Many now have options for view creation instead of copying data.
The depth of the data copying may have also changed.

One View example is ``G.nodes`` (or ``G.nodes()``) which now returns a
dict-like NodeView while ``G.nodes_iter()`` has been removed. Similarly
for views with ``G.edges`` and removing ``G.edges_iter``.
The Graph attributes ``G.node`` and ``G.edge`` have been removed in favor of
using ``G.nodes[n]`` and ``G.edges[u, v]``.
Finally, the ``selfloop`` methods and ``add_path``/``star``/``cycle`` have
been moved from graph methods to networkx functions.

We expect that these changes will break some code. We have tried to make
them break the code in ways that raise exceptions, so it will be obvious
that code is broken.

There are also a number of improvements to the codebase outside of the base
graph classes. These are too numerous to catalog here, but a couple obvious
ones include:

- centering of nodes in ``drawing/nx_pylab``,
- iterator vs dict output from a few ``shortest_path`` routines

-------

Some demonstrations:

    >>> import networkx as nx
    >>> G = nx.complete_graph(5)
    >>> G.nodes  # for backward compatibility G.nodes() works as well
    NodeView((0, 1, 2, 3, 4))

You can iterate through ``G.nodes`` (or ``G.nodes()``)

    >>> for node in G.nodes:
    ...     print(node)
    0
    1
    2
    3
    4

If you want a list of nodes you can use the Python list function

    >>> list(G.nodes)
    [0, 1, 2, 3, 4]

``G.nodes`` is set-like allowing set operations. It is also dict-like in that you
can look up node data with ``G.nodes[n]['weight']``. You can still use the calling
interface ``G.nodes(data='weight')`` to iterate over node/data pairs. In addition
to the dict-like views ``keys``/``values``/``items``, ``G.nodes`` has a data-view
G.nodes.data('weight').  The new EdgeView ``G.edges`` has similar features for edges.

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

DiGraphViews behave similar to GraphViews, but have a few more methods.

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

-------

Some methods have been removed from the base graph class and placed into the main
networkx namespace. These are:  ``G.add_path``, ``G.add_star``, ``G.add_cycle``,
``G.number_of_selfloops``, ``G.nodes_with_selfloops``, and ``G.selfloop_edges``.
These are replaced by ``nx.path_graph(G, ...)`` ``nx.add_star(G, ...)``,
``nx.selfloop_edges(G)``, etc.

-------

Writing code that works for both versions
=========================================

Methods ``set_node_attributes``/``get_node_attributes``/``set_edge_attributes``/``get_edge_attributes``
have changed the order of their keyword arguments ``name`` and ``value``. So, to make it
work with both versions you should use the keywords in your call.

    >>> nx.set_node_attributes(G, value=1.0, name='weight')

Graph attribute ``edge`` has been removed. It should be replaced with ``G.adj`` which is
bascially the same as v1's ``G.edge`` in both v1 and v2.

Change any method with ``_iter`` in its name to the version without ``_iter``.
In v1 you will replace an iterator by a list, so its slower but the code will still work.
In v2 you will get a view (which acts like an iterator).

The methods moved from the graph classes and put into the main package namespace
are hard to get to work with both versions. You can code for the namespace version
and add code to the v1 namespace in an ad hoc manner:

    >>> if nx.__version__[0] == '1':
    ...     nx.add_path = lambda G, nodes: G.add_path(nodes)
