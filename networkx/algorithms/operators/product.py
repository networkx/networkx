"""
Graph products.
"""
#    Copyright (C) 2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
from itertools import product

__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'
                            'Ben Edwards(bedwards@cs.unm.edu)'])

__all__ = ['tensor_product', 'cartesian_product',
           'lexicographic_product', 'strong_product', 'power']


def _dict_product(d1, d2):
    return dict((k, (d1.get(k), d2.get(k))) for k in set(d1) | set(d2))


# Generators for producting graph products
def _node_product(G, H):
    for u, v in product(G, H):
        yield ((u, v), _dict_product(G.node[u], H.node[v]))


def _directed_edges_cross_edges(G, H):
    if not G.is_multigraph() and not H.is_multigraph():
        for u, v, c in G.edges_iter(data=True):
            for x, y, d in H.edges_iter(data=True):
                yield (u, x), (v, y), _dict_product(c, d)
    if not G.is_multigraph() and H.is_multigraph():
        for u, v, c in G.edges_iter(data=True):
            for x, y, k, d in H.edges_iter(data=True, keys=True):
                yield (u, x), (v, y), k, _dict_product(c, d)
    if G.is_multigraph() and not H.is_multigraph():
        for u, v, k, c in G.edges_iter(data=True, keys=True):
            for x, y, d in H.edges_iter(data=True):
                yield (u, x), (v, y), k, _dict_product(c, d)
    if G.is_multigraph() and H.is_multigraph():
        for u, v, j, c in G.edges_iter(data=True, keys=True):
            for x, y, k, d in H.edges_iter(data=True, keys=True):
                yield (u, x), (v, y), (j, k), _dict_product(c, d)


def _undirected_edges_cross_edges(G, H):
    if not G.is_multigraph() and not H.is_multigraph():
        for u, v, c in G.edges_iter(data=True):
            for x, y, d in H.edges_iter(data=True):
                yield (v, x), (u, y), _dict_product(c, d)
    if not G.is_multigraph() and H.is_multigraph():
        for u, v, c in G.edges_iter(data=True):
            for x, y, k, d in H.edges_iter(data=True, keys=True):
                yield (v, x), (u, y), k, _dict_product(c, d)
    if G.is_multigraph() and not H.is_multigraph():
        for u, v, k, c in G.edges_iter(data=True, keys=True):
            for x, y, d in H.edges_iter(data=True):
                yield (v, x), (u, y), k, _dict_product(c, d)
    if G.is_multigraph() and H.is_multigraph():
        for u, v, j, c in G.edges_iter(data=True, keys=True):
            for x, y, k, d in H.edges_iter(data=True, keys=True):
                yield (v, x), (u, y), (j, k), _dict_product(c, d)


def _edges_cross_nodes(G, H):
    if G.is_multigraph():
        for u, v, k, d in G.edges_iter(data=True, keys=True):
            for x in H:
                yield (u, x), (v, x), k, d
    else:
        for u, v, d in G.edges_iter(data=True):
            for x in H:
                if H.is_multigraph():
                    yield (u, x), (v, x), None, d
                else:
                    yield (u, x), (v, x), d


def _nodes_cross_edges(G, H):
    if H.is_multigraph():
        for x in G:
            for u, v, k, d in H.edges_iter(data=True, keys=True):
                yield (x, u), (x, v), k, d
    else:
        for x in G:
            for u, v, d in H.edges_iter(data=True):
                if G.is_multigraph():
                    yield (x, u), (x, v), None, d
                else:
                    yield (x, u), (x, v), d


def _edges_cross_nodes_and_nodes(G, H):
    if G.is_multigraph():
        for u, v, k, d in G.edges_iter(data=True, keys=True):
            for x in H:
                for y in H:
                    yield (u, x), (v, y), k, d
    else:
        for u, v, d in G.edges_iter(data=True):
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


def tensor_product(G, H):
    r"""Return the tensor product of G and H.

    The tensor product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, $V(P)=V(G) \times V(H)$.
    P has an edge ((u,v),(x,y)) if and only if (u,v) is an edge in G
    and (x,y) is an edge in H.

    Sometimes referred to as the categorical product. 


    Parameters
    ----------
    G, H: graphs
     Networkx graphs. 

    Returns
    -------
    P: NetworkX graph
     The tensor product of G and H. P will be a multi-graph if either G
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

    For example
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

    The tensor product P of the graphs G and H has a node set that
    is the Cartesian product of the node sets, $V(P)=V(G) \times V(H)$.
    P has an edge ((u,v),(x,y)) if and only if (u,v) is an edge in G 
    and x==y or  and (x,y) is an edge in H and u==v.
    and (x,y) is an edge in H.

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

    For example
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

    For example
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

    For example
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


def power(G, k):
    """Returns the specified power of a graph.

    ..
       The *k*th power of a simple graph *G* = (*V*, *E*) is the graph
       *G<sup>k</sup>* whose vertex set is *V*, two distinct vertices being
       adjacent in *G<sup>k</sup>* if and only if their [shortest path]
       distance in *G* is at most *k*.
       -- Exercise 3.1.6 of *Graph Theory* by J. A. Bondy and U. S. R. Murty
          [1]_

    Parameters
    ----------
    G: graph
      A NetworkX simple graph object.
    k: positive integer
      The power to which to raise the graph `G`.

    Returns
    -------
    NetworkX simple graph
      `G` to the `k`th power.

    Raises
    ------
    :exc:`ValueError`
      If the exponent `k` is not positive.

    NetworkXError
      If G is not a simple graph.

    Examples
    --------
    >>> G = nx.path_graph(4)
    >>> nx.power(G,2).edges()
    [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
    >>> nx.power(G,3).edges()
    [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]

    A complete graph of order n is returned if *k* is greater than equal to n/2
    for a cycle graph of even order n, and if *k* is greater than equal to
    (n-1)/2 for a cycle graph of odd order.

    >>> G = nx.cycle_graph(5)
    >>> nx.power(G,2).edges() == nx.complete_graph(5).edges()
    True
    >>> G = nx.cycle_graph(8)
    >>> nx.power(G,4).edges() == nx.complete_graph(8).edges()
    True

    References
    ----------
    .. [1] J. A. Bondy, U. S. R. Murty:
       Graph Theory.
       Springer, 2008.
    """
    if k <= 0:
        raise ValueError('k must be a positive integer')
    if G.is_multigraph() or G.is_directed():
        raise nx.NetworkXError("G should be a simple graph")
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
            if (k <= level):
                break
            level = level + 1
        H.add_edges_from((n, nbr) for nbr in seen)
    return H
