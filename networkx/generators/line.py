"""Functions for generating line graphs.

"""
#    Copyright (C) 2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__ = "\n".join(["Aric Hagberg (hagberg@lanl.gov)",
                        "Pieter Swart (swart@lanl.gov)",
                        "Dan Schult (dschult@colgate.edu)",
                        "chebee7i (chebee7i@gmail.com)"])

__all__ = ['line_graph']


def line_graph(G, create_using=None):
    """Returns the line graph of the graph or digraph ``G``.

    The line graph of a graph ``G`` has a node for each edge in ``G`` and an
    edge joining those nodes if the two edges in ``G`` share a common node. For
    directed graphs, nodes are adjacent exactly when the edges they represent
    form a directed path of length two.

    The nodes of the line graph are 2-tuples of nodes in the original graph (or
    3-tuples for multigraphs, with the key of the edge as the third element).

    For information about self-loops and more discussion, see the **Notes**
    section below.

    Parameters
    ----------
    G : graph
        A NetworkX Graph, DiGraph, MultiGraph, or MultiDigraph.

    Returns
    -------
    L : graph
        The line graph of G.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.star_graph(3)
    >>> L = nx.line_graph(G)
    >>> print(sorted(map(sorted, L.edges())))  # makes a 3-clique, K3
    [[(0, 1), (0, 2)], [(0, 1), (0, 3)], [(0, 2), (0, 3)]]

    Notes
    -----
    Graph, node, and edge data are not propagated to the new graph. For
    undirected graphs, the nodes in G must be sortable, otherwise the
    constructed line graph may not be correct.

    *Self-loops in undirected graphs*

    For an undirected graph `G` without multiple edges, each edge can be
    written as a set `\{u, v\}`.  Its line graph `L` has the edges of `G` as
    its nodes. If `x` and `y` are two nodes in `L`, then `\{x, y\}` is an edge
    in `L` if and only if the intersection of `x` and `y` is nonempty. Thus,
    the set of all edges is determined by the set of all pairwise intersections
    of edges in `G`.

    Trivially, every edge in G would have a nonzero intersection with itself,
    and so every node in `L` should have a self-loop. This is not so
    interesting, and the original context of line graphs was with simple
    graphs, which had no self-loops or multiple edges. The line graph was also
    meant to be a simple graph and thus, self-loops in `L` are not part of the
    standard definition of a line graph. In a pairwise intersection matrix,
    this is analogous to excluding the diagonal entries from the line graph
    definition.

    Self-loops and multiple edges in `G` add nodes to `L` in a natural way, and
    do not require any fundamental changes to the definition. It might be
    argued that the self-loops we excluded before should now be included.
    However, the self-loops are still "trivial" in some sense and thus, are
    usually excluded.

    *Self-loops in directed graphs*

    For a directed graph `G` without multiple edges, each edge can be written
    as a tuple `(u, v)`. Its line graph `L` has the edges of `G` as its
    nodes. If `x` and `y` are two nodes in `L`, then `(x, y)` is an edge in `L`
    if and only if the tail of `x` matches the head of `y`, for example, if `x
    = (a, b)` and `y = (b, c)` for some vertices `a`, `b`, and `c` in `G`.

    Due to the directed nature of the edges, it is no longer the case that
    every edge in `G` should have a self-loop in `L`. Now, the only time
    self-loops arise is if a node in `G` itself has a self-loop.  So such
    self-loops are no longer "trivial" but instead, represent essential
    features of the topology of `G`. For this reason, the historical
    development of line digraphs is such that self-loops are included. When the
    graph `G` has multiple edges, once again only superficial changes are
    required to the definition.

    References
    ----------
    * Harary, Frank, and Norman, Robert Z., "Some properties of line digraphs",
      Rend. Circ. Mat. Palermo, II. Ser. 9 (1960), 161--168.
    * Hemminger, R. L.; Beineke, L. W. (1978), "Line graphs and line digraphs",
      in Beineke, L. W.; Wilson, R. J., Selected Topics in Graph Theory,
      Academic Press Inc., pp. 271--305.

    """
    if G.is_directed():
        L = _lg_directed(G, create_using=create_using)
    else:
        L = _lg_undirected(G, selfloops=False, create_using=create_using)
    return L

def _node_func(G):
    """Returns a function which returns a sorted node for line graphs.

    When constructing a line graph for undirected graphs, we must normalize
    the ordering of nodes as they appear in the edge.

    """
    if G.is_multigraph():
        def sorted_node(u, v, key):
            return (u, v, key) if u <= v else (v, u, key)
    else:
        def sorted_node(u, v):
            return (u, v) if u <= v else (v, u)
    return sorted_node

def _edge_func(G):
    """Returns the edges from G, handling keys for multigraphs as necessary.

    """
    if G.is_multigraph():
        def get_edges(nbunch=None):
            return G.edges_iter(nbunch, keys=True)
    else:
        def get_edges(nbunch=None):
            return G.edges_iter(nbunch)
    return get_edges

def _sorted_edge(u, v):
    """Returns a sorted edge.

    During the construction of a line graph for undirected graphs, the data
    structure can be a multigraph even though the line graph will never have
    multiple edges between its nodes.  For this reason, we must make sure not
    to add any edge more than once.  This requires that we build up a list of
    edges to add and then remove all duplicates.  And so, we must normalize
    the representation of the edges.

    """
    return (u, v) if u <= v else (v, u)

def _lg_directed(G, create_using=None):
    """Return the line graph L of the (multi)digraph G.

    Edges in G appear as nodes in L, represented as tuples of the form (u,v)
    or (u,v,key) if G is a multidigraph. A node in L corresponding to the edge
    (u,v) is connected to every node corresponding to an edge (v,w).

    Parameters
    ----------
    G : digraph
        A directed graph or directed multigraph.
    create_using : None
        A digraph instance used to populate the line graph.

    """
    if create_using is None:
        L = G.__class__()
    else:
        L = create_using

    # Create a graph specific edge function.
    get_edges = _edge_func(G)

    for from_node in get_edges():
        # from_node is: (u,v) or (u,v,key)
        L.add_node(from_node)
        for to_node in get_edges(from_node[1]):
            L.add_edge(from_node, to_node)

    return L

def _lg_undirected(G, selfloops=False, create_using=None):
    """Return the line graph L of the (multi)graph G.

    Edges in G appear as nodes in L, represented as sorted tuples of the form
    (u,v), or (u,v,key) if G is a multigraph. A node in L corresponding to
    the edge {u,v} is connected to every node corresponding to an edge that
    involves u or v.

    Parameters
    ----------
    G : graph
        An undirected graph or multigraph.
    selfloops : bool
        If `True`, then self-loops are included in the line graph. If `False`,
        they are excluded.
    create_using : None
        A graph instance used to populate the line graph.

    Notes
    -----
    The standard algorithm for line graphs of undirected graphs does not
    produce self-loops.

    """
    if create_using is None:
        L = G.__class__()
    else:
        L = create_using

    # Graph specific functions for edges and sorted nodes.
    get_edges = _edge_func(G)
    sorted_node = _node_func(G)

    # Determine if we include self-loops or not.
    shift = 0 if selfloops else 1

    edges = set([])
    for u in G:
        # Label nodes as a sorted tuple of nodes in original graph.
        nodes = [ sorted_node(*x) for x in get_edges(u) ]

        if len(nodes) == 1:
            # Then the edge will be an isolated node in L.
            L.add_node(nodes[0])

        # Add a clique of `nodes` to graph. To prevent double adding edges,
        # especially important for multigraphs, we store the edges in
        # canonical form in a set.
        for i, a in enumerate(nodes):
            edges.update([ _sorted_edge(a,b) for b in nodes[i+shift:] ])

    L.add_edges_from(edges)
    return L
