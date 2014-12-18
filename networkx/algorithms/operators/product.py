#    Copyright (C) 2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#
# Authors:
#     Aric Hagberg <hagberg@lanl.gov>
#     Pieter Swart <swart@lanl.gov>
#     Dan Schult <dschult@colgate.edu>
#     Ben Edwards <bedwards@cs.unm.edu>
"""
Graph products.
"""
from itertools import chain
from itertools import combinations_with_replacement
from itertools import product

try:
    import scipy
except:
    scipy_is_available = False
else:
    scipy_is_available = True

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['tensor_product', 'cartesian_product', 'lexicographic_product',
           'power', 'strong_product', 'walk_power']


def _dict_product(d1, d2):
    return dict((k, (d1.get(k), d2.get(k))) for k in set(d1) | set(d2))


# Generators for producting graph products
def _node_product(G, H):
    for u, v in product(G, H):
        yield ((u, v), _dict_product(G.node[u], H.node[v]))


def _directed_edges_cross_edges(G, H):
    if not G.is_multigraph() and not H.is_multigraph():
        for u, v, c in G.edges(data=True):
            for x, y, d in H.edges(data=True):
                yield (u, x), (v, y), _dict_product(c, d)
    if not G.is_multigraph() and H.is_multigraph():
        for u, v, c in G.edges(data=True):
            for x, y, k, d in H.edges(data=True, keys=True):
                yield (u, x), (v, y), k, _dict_product(c, d)
    if G.is_multigraph() and not H.is_multigraph():
        for u, v, k, c in G.edges(data=True, keys=True):
            for x, y, d in H.edges(data=True):
                yield (u, x), (v, y), k, _dict_product(c, d)
    if G.is_multigraph() and H.is_multigraph():
        for u, v, j, c in G.edges(data=True, keys=True):
            for x, y, k, d in H.edges(data=True, keys=True):
                yield (u, x), (v, y), (j, k), _dict_product(c, d)


def _undirected_edges_cross_edges(G, H):
    if not G.is_multigraph() and not H.is_multigraph():
        for u, v, c in G.edges(data=True):
            for x, y, d in H.edges(data=True):
                yield (v, x), (u, y), _dict_product(c, d)
    if not G.is_multigraph() and H.is_multigraph():
        for u, v, c in G.edges(data=True):
            for x, y, k, d in H.edges(data=True, keys=True):
                yield (v, x), (u, y), k, _dict_product(c, d)
    if G.is_multigraph() and not H.is_multigraph():
        for u, v, k, c in G.edges(data=True, keys=True):
            for x, y, d in H.edges(data=True):
                yield (v, x), (u, y), k, _dict_product(c, d)
    if G.is_multigraph() and H.is_multigraph():
        for u, v, j, c in G.edges(data=True, keys=True):
            for x, y, k, d in H.edges(data=True, keys=True):
                yield (v, x), (u, y), (j, k), _dict_product(c, d)


def _edges_cross_nodes(G, H):
    if G.is_multigraph():
        for u, v, k, d in G.edges(data=True, keys=True):
            for x in H:
                yield (u, x), (v, x), k, d
    else:
        for u, v, d in G.edges(data=True):
            for x in H:
                if H.is_multigraph():
                    yield (u, x), (v, x), None, d
                else:
                    yield (u, x), (v, x), d


def _nodes_cross_edges(G, H):
    if H.is_multigraph():
        for x in G:
            for u, v, k, d in H.edges(data=True, keys=True):
                yield (x, u), (x, v), k, d
    else:
        for x in G:
            for u, v, d in H.edges(data=True):
                if G.is_multigraph():
                    yield (x, u), (x, v), None, d
                else:
                    yield (x, u), (x, v), d


def _edges_cross_nodes_and_nodes(G, H):
    if G.is_multigraph():
        for u, v, k, d in G.edges(data=True, keys=True):
            for x in H:
                for y in H:
                    yield (u, x), (v, y), k, d
    else:
        for u, v, d in G.edges(data=True):
            for x in H:
                for y in H:
                    if H.is_multigraph():
                        yield (u, x), (v, y), None, d
                    else:
                        yield (u, x), (v, y), d


def _init_product_graph(G, H):
    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")
    if G.is_multigraph() or H.is_multigraph():
        GH = nx.MultiGraph()
    else:
        GH = nx.Graph()
    if G.is_directed():
        GH = GH.to_directed()
    return GH


def _walk_power_networkx(G, k, parallel_edges=True, create_using=None):
    """Computes the specified walk power of the graph.

    This function uses only pure NetworkX functionality (no SciPy) to
    compute the *k*th walk power of *G*.

    """
    # By default, the output should be a multigraph.
    if create_using is None:
        create_using = (nx.MultiDiGraph() if G.is_directed()
                        else nx.MultiGraph())
    H = create_using
    H.clear()
    num_walks = nx.all_pairs_number_of_walks(G, k)
    # This function faces some of the same problems as
    # `nx.from_numpy_matrix` concerning parallel edges in multigraphs,
    # including the following.
    #
    # If we are creating an undirected multigraph, only add the edges
    # from the upper triangle of the adjacency matrix. Otherwise, add
    # all the edges.
    #
    # Without this check, we run into a problem where each edge is added
    # twice when ``H.add_edges_from()`` is invoked below.
    if H.is_multigraph() and not H.is_directed():
        pairs = combinations_with_replacement(G, 2)
    else:
        pairs = product(G, repeat=2)
    if H.is_multigraph() and parallel_edges:
        # The following lines are functionally equivalent to:
        #
        #     new_edges = []
        #     for u in G:
        #         for v in G:
        #             for n in range(num_walks[u][v]):
        #                 new_edges.append((u, v, dict(weight=1)))
        #
        new_edges = chain.from_iterable(((u, v, dict(weight=1))
                                         for n in range(num_walks[u][v]))
                                        for u, v in pairs)
    else:
        # Need to exclude length zero walks.
        new_edges = ((u, v, dict(weight=num_walks[u][v]))
                     for u, v in pairs if num_walks[u][v] > 0)
    H.add_nodes_from(G)
    H.add_edges_from(new_edges)
    return H


def _walk_power_scipy(G, k, parallel_edges=True, create_using=None):
    """Computes the specified walk power of the graph.

    This function uses SciPy to perform the exponentiation of the
    adjacency matrix of ``G``. It will raise an exception if SciPy is
    not available.

    """
    A = nx.adjacency_matrix(G)
    power = A ** k
    if create_using is None:
        create_using = (nx.MultiDiGraph() if G.is_directed()
                        else nx.MultiGraph())
    return nx.from_scipy_sparse_matrix(power, parallel_edges=parallel_edges,
                                       create_using=create_using)


def walk_power(G, k, parallel_edges=True, create_using=None):
    """Returns the specified "walk power" of a graph.

    The `k`th *walk power* of the graph `G` is a multigraph whose node
    set is the same as that of `G` and whose edge set is a multiset
    containing one edge from vertex ``u`` to vertex ``v`` for each walk
    of length `k` from ``u`` to ``v``.

    Parameters
    ----------
    G: graph

      A NetworkX graph object.

    k: non-negative integer

      The power to which to raise the graph `G`.

    parallel_edges : Boolean (default ``True``)

      If this is ``False`` and `create_using` is a multigraph, then instead of
      *d* parallel edges joining vertices, there will be a single edge with
      weight *d* in the returned graph, where *d* is the number of walks of
      length exactly `k` joining the vertices.

    create_using : a NetworkX Graph object

      The type of this graph will be used to construct the output graph. If
      this is an instance of :class:`networkx.Graph` or
      :class:`networkx.DiGraph`, then the `parallel_edges` keyword argument
      will be ignored (since any parallel edges will be collapsed to a single
      edge anyway).

    Returns
    -------
    NetworkX graph

      `G` to the `k`th walk power. If `create_using` is not ``None``, then the
      returned graph will have the same type as `create_using`. If
      `create_using` is ``None``, the returned graph will be a multigraph,
      directed if and only if `G` is directed.

    Raises
    ------
    :exc:`ValueError`

      If the exponent `k` is negative.

    Implementation
    --------------
    If SciPy is available, the returned graph is generated from the
    `k`th matrix power of the adjacency matrix of the input graph. If
    SciPy is not available, then we use a pure Python NetworkX algorithm
    that computes the number of walks of length exactly `k` joining each
    pair of vertices in the graph.

    Examples
    --------
    The second walk power of the path graph has a self-loop for each
    vertex on the ends, two self-loops for each internal vertex, and an
    edge joining each pair of vertices at distance two::

        >>> G = nx.path_graph(4)
        >>> list(G.edges())
        [(0, 1), (1, 2), (2, 3)]
        >>> H = nx.walk_power(G, 2)
        >>> list(H.edges())
        [(0, 0), (0, 2), (1, 1), (1, 1), (1, 3), (2, 2), (2, 2), (3, 3)]

    Force the output to be a simple graph instead of a multigraph
    (contrast with the previous example)::

        >>> G = nx.path_graph(4)
        >>> H = nx.walk_power(G, 2, create_using=nx.Graph())
        >>> list(H.edges())
        [(0, 0), (0, 2), (1, 1), (1, 3), (2, 2), (3, 3)]

    To force the returned graph to be a multigraph with a single
    weighted edge instead of multiple parallel edges, set the
    `parallel_edges` keyword argument to ``False``. In this example, the
    second walk power of the cycle graph on four vertices has two
    parallel self-loops on each vertex, and two parallel edges joining
    each pair of vertices at distance two. Each pair of parallel edges
    becomes a single edge (in an instance of
    :class:`networkx.MultiGraph`) with weight two::

        >>> G = nx.cycle_graph(4)
        >>> list(G.edges())
        [(0, 1), (0, 3), (1, 2), (2, 3)]
        >>> H = nx.walk_power(G, 2, parallel_edges=False)
        >>> list(H.edges())
        [(0, 0), (0, 2), (1, 1), (1, 3), (2, 2), (3, 3)]
        >>> H[0][0]
        {0: {'weight': 2}}

    """
    if k < 0:
        raise ValueError('exponent must be positive: {0}'.format(k))
    impl = _walk_power_scipy if scipy_is_available else _walk_power_networkx
    return impl(G, k, parallel_edges=parallel_edges, create_using=create_using)


def tensor_product(G, H):
    r"""Return the tensor product of G and H.

    The tensor product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, :math:`V(P)=V(G) \times V(H)`.
    P has an edge ((u,v),(x,y)) if and only if (u,x) is an edge in G
    and (v,y) is an edge in H.

    Tensor product is sometimes also referred to as the categorical product,
    direct product, cardinal product or conjunction.


    Parameters
    ----------
    G, H: graphs
     Networkx graphs.

    Returns
    -------
    P: NetworkX graph
     The tensor product of G and H. P will be a multi-graph if either G
     or H is a multi-graph, will be a directed if G and H are directed,
     and undirected if G and H are undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Node attributes in P are two-tuple of the G and H node attributes.
    Missing attributes are assigned None.

    Examples
    --------
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> P = nx.tensor_product(G,H)
    >>> list(P)
    [(0, 'a')]

    Edge attributes and edge keys (for multigraphs) are also copied to the
    new product graph
    """
    GH = _init_product_graph(G, H)
    GH.add_nodes_from(_node_product(G, H))
    GH.add_edges_from(_directed_edges_cross_edges(G, H))
    if not GH.is_directed():
        GH.add_edges_from(_undirected_edges_cross_edges(G, H))
    GH.name = "Tensor product(" + G.name + "," + H.name + ")"
    return GH


def cartesian_product(G, H):
    """Return the Cartesian product of G and H.

    The Cartesian product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, :math:`V(P)=V(G) \times V(H)`.
    P has an edge ((u,v),(x,y)) if and only if either u is equal to x and
    v & y are adjacent in H or if v is equal to y and u & x are adjacent in G.

    Parameters
    ----------
    G, H: graphs
     Networkx graphs.

    Returns
    -------
    P: NetworkX graph
     The Cartesian product of G and H. P will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if G and H are directed,
     and undirected if G and H are undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Node attributes in P are two-tuple of the G and H node attributes.
    Missing attributes are assigned None.

    Examples
    --------
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> P = nx.cartesian_product(G,H)
    >>> list(P)
    [(0, 'a')]

    Edge attributes and edge keys (for multigraphs) are also copied to the
    new product graph
    """
    if not G.is_directed() == H.is_directed():
        raise nx.NetworkXError("G and H must be both directed or",
                               "both undirected")
    GH = _init_product_graph(G, H)
    GH.add_nodes_from(_node_product(G, H))
    GH.add_edges_from(_edges_cross_nodes(G, H))
    GH.add_edges_from(_nodes_cross_edges(G, H))
    GH.name = "Cartesian product(" + G.name + "," + H.name + ")"
    return GH


def lexicographic_product(G, H):
    """Return the lexicographic product of G and H.

    The lexicographical product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, $V(P)=V(G) \times V(H)$.
    P has an edge ((u,v),(x,y)) if and only if (u,v) is an edge in G
    or u==v and (x,y) is an edge in H.

    Parameters
    ----------
    G, H: graphs
     Networkx graphs.

    Returns
    -------
    P: NetworkX graph
     The Cartesian product of G and H. P will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if G and H are directed,
     and undirected if G and H are undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Node attributes in P are two-tuple of the G and H node attributes.
    Missing attributes are assigned None.

    Examples
    --------
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> P = nx.lexicographic_product(G,H)
    >>> list(P)
    [(0, 'a')]

    Edge attributes and edge keys (for multigraphs) are also copied to the
    new product graph
    """
    GH = _init_product_graph(G, H)
    GH.add_nodes_from(_node_product(G, H))
    # Edges in G regardless of H designation
    GH.add_edges_from(_edges_cross_nodes_and_nodes(G, H))
    # For each x in G, only if there is an edge in H
    GH.add_edges_from(_nodes_cross_edges(G, H))
    GH.name = "Lexicographic product(" + G.name + "," + H.name + ")"
    return GH


def strong_product(G, H):
    """Return the strong product of G and H.

    The strong product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, $V(P)=V(G) \times V(H)$.
    P has an edge ((u,v),(x,y)) if and only if
    u==v and (x,y) is an edge in H, or
    x==y and (u,v) is an edge in G, or
    (u,v) is an edge in G and (x,y) is an edge in H.

    Parameters
    ----------
    G, H: graphs
     Networkx graphs.

    Returns
    -------
    P: NetworkX graph
     The Cartesian product of G and H. P will be a multi-graph if either G
     or H is a multi-graph. Will be a directed if G and H are directed,
     and undirected if G and H are undirected.

    Raises
    ------
    NetworkXError
     If G and H are not both directed or both undirected.

    Notes
    -----
    Node attributes in P are two-tuple of the G and H node attributes.
    Missing attributes are assigned None.

    Examples
    --------
    >>> G = nx.Graph()
    >>> H = nx.Graph()
    >>> G.add_node(0,a1=True)
    >>> H.add_node('a',a2='Spam')
    >>> P = nx.strong_product(G,H)
    >>> list(P)
    [(0, 'a')]

    Edge attributes and edge keys (for multigraphs) are also copied to the
    new product graph
    """
    GH = _init_product_graph(G, H)
    GH.add_nodes_from(_node_product(G, H))
    GH.add_edges_from(_nodes_cross_edges(G, H))
    GH.add_edges_from(_edges_cross_nodes(G, H))
    GH.add_edges_from(_directed_edges_cross_edges(G, H))
    if not GH.is_directed():
        GH.add_edges_from(_undirected_edges_cross_edges(G, H))
    GH.name = "Strong product(" + G.name + "," + H.name + ")"
    return GH


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def power(G, k):
    """Returns the specified power of a graph.

    The `k`th power of a simple graph `G`, denoted :math:`G^k`, is a
    graph on the same set of nodes in which two distinct nodes *u* and
    *v* are adjacent in :math:`G^k` if and only if the shortest path
    distance between *u* and *v* in `G` is at most `k`.

    Parameters
    ----------
    G : graph
        A NetworkX simple graph object.

    k : positive integer
        The power to which to raise the graph `G`.

    Returns
    -------
    NetworkX simple graph
        `G` to the `k`th power.

    Raises
    ------
    ValueError
        If the exponent `k` is not positive.

    NetworkXNotImplemented
        If `G` is not a simple graph.

    Examples
    --------
    The number of edges will never decrease when taking successive
    powers::

        >>> G = nx.path_graph(4)
        >>> list(nx.power(G, 2).edges())
        [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
        >>> list(nx.power(G, 3).edges())
        [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    The `k`th power of a cycle graph on *n* nodes is the complete graph
    on *n* nodes, if `k` is at least ``n // 2``::

        >>> G = nx.cycle_graph(5)
        >>> H = nx.complete_graph(5)
        >>> nx.is_isomorphic(nx.power(G, 2), H)
        True
        >>> G = nx.cycle_graph(8)
        >>> H = nx.complete_graph(8)
        >>> nx.is_isomorphic(nx.power(G, 4), H)
        True

    References
    ----------
    .. [1] J. A. Bondy, U. S. R. Murty, *Graph Theory*. Springer, 2008.

    Notes
    -----
    This definition of "power graph" comes from Exercise 3.1.6 of *Graph
    Theory* by Bondy and Murty [1]_.

    """
    if k <= 0:
        raise ValueError('k must be a positive integer')
    H = nx.Graph()
    # update BFS code to ignore self loops.
    for n in G:
        seen = {}                  # level (number of hops) when seen in BFS
        level = 1                  # the current level
        nextlevel = G[n]
        while nextlevel:
            thislevel = nextlevel  # advance to next level
            nextlevel = {}         # and start a new list (fringe)
            for v in thislevel:
                if v == n:         # avoid self loop
                    continue
                if v not in seen:
                    seen[v] = level         # set the level of vertex v
                    nextlevel.update(G[v])  # add neighbors of v
            if k <= level:
                break
            level += 1
        H.add_edges_from((n, nbr) for nbr in seen)
    return H
