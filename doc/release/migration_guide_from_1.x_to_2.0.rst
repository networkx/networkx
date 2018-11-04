:orphan:

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
We have changed many methods from reporting lists or dicts to iterating over
the information. Most of the changes in this regard are in the base classes.
Methods that used to return containers now return views (inspired from
`dictionary views <https://docs.python.org/3/library/stdtypes.html#dict-views>`_
in Python) and methods that returned an iterator have been removed.
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

``G.degree`` now returns a DegreeView. This is less dict-like than the other views
in the sense that it iterates over (node, degree) pairs, does not provide
keys/values/items/get methods. It does provide lookup ``G.degree[n]`` and
``(node, degree)`` iteration. A dict keyed by nodes to degree values can be
easily created if needed as ``dict(G.degree)``.

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
for directed graphs. If you want just the degree values, here are some options.
They are shown for ``in_degree`` of a ``DiGraph``, but similar ideas work
for ``out_degree`` and ``degree``

    >>> DG = nx.DiGraph()
    >>> DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
    >>> deg = DG.in_degree   # sets up the view
    >>> [d for n, d in deg]   # gets all nodes' degree values
    [1, 1, 0]
    >>> (d for n, d in deg)    # iterator over degree values
    <generator object <genexpr> ...>
    >>> [deg[n] for n in [1, 3]]   # using lookup for only some nodes
    [1, 0]

    >>> dict(DG.in_degree([1, 3])).values()    # works for nx-1 and nx-2
    [1, 0]
    >>> # DG.in_degree(nlist) creates a restricted view for only nodes in nlist.
    >>> # but see the fourth option above for using lookup instead.
    >>> list(d for n, d in DG.in_degree([1, 3]))
    [1, 0]

    >>> [len(nbrs) for n, nbrs in DG.pred.items()]  # probably slightly fastest for all nodes
    [1, 1, 0]
    >>> [len(DG.pred[n]) for n in [1, 3]]           # probably slightly faster for only some nodes
    [1, 0]

-------

If ``n`` is a node in ``G``, then ``G.neighbors(n)`` returns an iterator.

    >>> n = 1
    >>> G.neighbors(n)
    <dictionary-keyiterator object at ...>
    >>> list(G.neighbors(n))
    [0, 2, 3, 4]

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

Some methods have been moved from the base graph class into the main namespace.
These are:  ``G.add_path``, ``G.add_star``, ``G.add_cycle``, ``G.number_of_selfloops``,
``G.nodes_with_selfloops``, and ``G.selfloop_edges``.
They are replaced by ``nx.path_graph(G, ...)`` ``nx.add_star(G, ...)``,
``nx.selfloop_edges(G)``, etc.
For backward compatibility, we are leaving them as deprecated methods.

-------

With the new GraphViews (SubGraph, ReversedGraph, etc) you can't assume that
``G.__class__()`` will create a new instance of the same graph type as ``G``.
In fact, the call signature for ``__class__`` differs depending on whether ``G``
is a view or a base class. For v2.x you should use ``G.fresh_copy()`` to
create a null graph of the correct type---ready to fill with nodes and edges.

Graph views can also be views-of-views-of-views-of-graphs. If you want to find the
original graph at the end of this chain use ``G.root_graph``. Be careful though
because it may be a different graph type (directed/undirected) than the view.

-------

``topolgical_sort``  no longer accepts ``reverse`` or ``nbunch`` arguments.
If ``nbunch`` was a single node source, then the same effect can now be achieved
using the ``subgraph`` operator:

    nx.topological_sort(G.subgraph(nx.descendants(G, nbunch)))

To achieve a reverse topological sort, the output should be converted to a list:

    reversed(list(nx.topological_sort(G)))

-------

Writing code that works for both versions
=========================================

Methods ``set_node_attributes``/``get_node_attributes``/``set_edge_attributes``/``get_edge_attributes``
have changed the order of their keyword arguments ``name`` and ``values``. So, to make it
work with both versions you should use the keywords in your call.

    >>> nx.set_node_attributes(G, values=1.0, name='weight')

-------

Change any method with ``_iter`` in its name to the version without ``_iter``.
In v1 this replaces an iterator by a list, but the code will still work.
In v2 this creates a view (which acts like an iterator).

-------

Replace any use of ``G.edge`` with ``G.adj``. The Graph attribute ``edge``
has been removed. The attribute ``G.adj`` is ``G.edge`` in v1 and will work
with both versions.

-------

If you use ``G.node.items()`` or similar in v1.x, you can replace it with
``G.nodes(data=True)`` which works for v2.x and v1.x.  Iterating over ``G.node```
as in ``for n in G.node:`` can be replaced with ``G``, as in: ``for n in G:``.

-------

The Graph attribute ``node`` has moved its functionality to ``G.nodes``, so code
expected to work with v2.x should use ``G.nodes``.
In fact most uses of ``G.node`` can be replaced by an idiom that works for both
versions. The functionality that can't easily is: ``G.node[n]``.
In v2.x that becomes ``G.nodes[n]`` which doesn't work in v1.x.

Luckily you can still use ``G.node[n]`` in v2.x when you want it to be able to work
with v1.x too. We have left ``G.node`` in v2.x as a transition pointer to ``G.nodes``.
We envision removing ``G.node`` in v3.x (sometime in the future).

-------

Copying node attribute dicts directly from one graph to another can corrupt
the node data structure if not done correctly. Code such as the following:

    >>> # dangerous in v1.x, not allowed in v2.x
    >>> G.node[n] = H.node[n]  # doctest: +SKIP

used to work, even though it could cause errors if ``n`` was not a node in ``G``.
That code will cause an error in v2.x.  Replace it with one of the more safe versions:

    >>> G.node[n].update(H.node[n])  # works in both v1.x and v2.x
    >>> G.nodes[n].update(H.nodes[n])  # works in v2.x

-------

The methods removed from the graph classes and put into the main package namespace
can be used via the associated deprecated methods. If you want to update your code
to the new functions, one hack to make that work with both versions is to write
your code for v2.x and add code to the v1 namespace in an ad hoc manner:

    >>> if nx.__version__[0] == '1':
    ...     nx.add_path = lambda G, nodes: G.add_path(nodes)

Similarly, v2.x code that uses ``G.fresh_copy()`` or ``G.root_graph`` is hard to make
work for v1.x. It may be best in this case to determine the graph type you want
explicitly and call Graph/DiGraph/MultiGraph/MultiDiGraph directly.

Using Pickle with v1 and v2
===========================

The Pickle protocol does not store class methods, only the data. So if you write a
pickle file with v1 you should not expect to read it into a v2 Graph. If this happens
to you, read it in with v1 installed and write a file with the node and edge
information. You can read that into a config with v2 installed and then add those nodes
and edges to a fresh graph. Try something similar to this:

    >>> # in v1.x
    >>> pickle.dump([G.nodes(data=True), G.edges(data=True)], file)  # doctest: +SKIP
    >>> # then in v2.x
    >>> nodes, edges = pickle.load(file)  # doctest: +SKIP
    >>> G = nx.Graph()  # doctest: +SKIP
    >>> G.add_nodes_from(nodes)  # doctest: +SKIP
    >>> G.add_edges_from(edges)  # doctest: +SKIP
