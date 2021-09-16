"""Algorithms related to reachability problems"""
import networkx as nx

__all__ = [
    "descendants",
    "ancestors",
    "transitive_closure",
    "descendants_at_distance",
]


def descendants(G, source):
    """Returns all nodes reachable from `source` in `G`.

    Parameters
    ----------
    G : NetworkX Graph
    source : node in `G`

    Returns
    -------
    set()
        The descendants of `source` in `G`

    Raises
    ------
    NetworkXError
        If node `source` is not in `G`.

    Examples
    --------
    >>> DG = nx.path_graph(5, create_using=nx.DiGraph)
    >>> sorted(list(nx.descendants(DG, 2)))
    [3, 4]

    See also
    --------
    ancestors
    """
    return {child for parent, child in nx.bfs_edges(G, source)}


def ancestors(G, source):
    """Returns all nodes having a path to `source` in `G`.

    Parameters
    ----------
    G : NetworkX Graph
    source : node in `G`

    Returns
    -------
    set()
        The ancestors of `source` in `G`

    Raises
    ------
    NetworkXError
        If node `source` is not in `G`.

    Examples
    --------
    >>> DG = nx.path_graph(5, create_using=nx.DiGraph)
    >>> sorted(list(nx.ancestors(DG, 2)))
    [0, 1]

    See also
    --------
    descendants
    """
    return {child for parent, child in nx.bfs_edges(G, source, reverse=True)}


def transitive_closure(G, reflexive=False):
    """Returns transitive closure of a directed graph

    The transitive closure of G = (V,E) is a graph G+ = (V,E+) such that
    for all v, w in V there is an edge (v, w) in E+ if and only if there
    is a path from v to w in G.

    Handling of paths from v to v has some flexibility within this definition.
    A reflexive transitive closure creates a self-loop for the path
    from v to v of length 0. The usual transitive closure creates a
    self-loop only if a cycle exists (a path from v to v with length > 0).
    We also allow an option for no self-loops.

    Parameters
    ----------
    G : NetworkX DiGraph
        A directed graph
    reflexive : Bool or None, optional (default: False)
        Determines when cycles create self-loops in the Transitive Closure.
        If True, trivial cycles (length 0) create self-loops. The result
        is a reflexive tranistive closure of G.
        If False (the default) non-trivial cycles create self-loops.
        If None, self-loops are not created.

    Returns
    -------
    NetworkX DiGraph
        The transitive closure of `G`

    Raises
    ------
    NetworkXNotImplemented
        If `G` is not directed

    Examples
    --------
    The treatment of trivial (i.e. length 0) cycles is controlled by the
    `reflexive` parameter.

    Trivial (i.e. length 0) cycles do not create self-loops when
    ``reflexive=False`` (the default)::

        >>> DG = nx.DiGraph([(1, 2), (2, 3)])
        >>> TC = nx.transitive_closure(DG, reflexive=False)
        >>> TC.edges()
        OutEdgeView([(1, 2), (1, 3), (2, 3)])

    However, nontrivial (i.e. length greater then 0) cycles create self-loops
    when ``reflexive=False`` (the default)::

        >>> DG = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
        >>> TC = nx.transitive_closure(DG, reflexive=False)
        >>> TC.edges()
        OutEdgeView([(1, 2), (1, 3), (1, 1), (2, 3), (2, 1), (2, 2), (3, 1), (3, 2), (3, 3)])

    Trivial cycles (length 0) create self-loops when ``reflexive=True``::

        >>> DG = nx.DiGraph([(1, 2), (2, 3)])
        >>> TC = nx.transitive_closure(DG, reflexive=True)
        >>> TC.edges()
        OutEdgeView([(1, 2), (1, 1), (1, 3), (2, 3), (2, 2), (3, 3)])

    And the third option is not to create self-loops at all when ``reflexive=None``::

        >>> DG = nx.DiGraph([(1, 2), (2, 3), (3, 1)])
        >>> TC = nx.transitive_closure(DG, reflexive=None)
        >>> TC.edges()
        OutEdgeView([(1, 2), (1, 3), (2, 3), (2, 1), (3, 1), (3, 2)])

    References
    ----------
    .. [1] https://www.ics.uci.edu/~eppstein/PADS/PartialOrder.py
    """
    if reflexive is None:
        TC = G.copy()
        for v in G:
            edges = ((v, u) for u in nx.dfs_preorder_nodes(G, v) if v != u)
            TC.add_edges_from(edges)
        return TC
    if reflexive is True:
        TC = G.copy()
        for v in G:
            edges = ((v, u) for u in nx.dfs_preorder_nodes(G, v))
            TC.add_edges_from(edges)
        return TC
    # reflexive is False
    TC = G.copy()
    for v in G:
        edges = ((v, w) for u, w in nx.edge_dfs(G, v))
        TC.add_edges_from(edges)
    return TC


def descendants_at_distance(G, source, distance):
    """Returns all nodes at a fixed `distance` from `source` in `G`.

    Parameters
    ----------
    G : NetworkX graph
        A graph
    source : node in `G`
    distance : the distance of the wanted nodes from `source`

    Returns
    -------
    set()
        The descendants of `source` in `G` at the given `distance` from `source`

    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> nx.descendants_at_distance(G, 2, 2)
    {0, 4}
    >>> H = nx.DiGraph()
    >>> H.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5), (2, 6)])
    >>> nx.descendants_at_distance(H, 0, 2)
    {3, 4, 5, 6}
    >>> nx.descendants_at_distance(H, 5, 0)
    {5}
    >>> nx.descendants_at_distance(H, 5, 1)
    set()
    """
    if not G.has_node(source):
        raise nx.NetworkXError(f"The node {source} is not in the graph.")
    current_distance = 0
    current_layer = {source}
    visited = {source}

    # this is basically BFS, except that the current layer only stores the nodes at
    # current_distance from source at each iteration
    while current_distance < distance:
        next_layer = set()
        for node in current_layer:
            for child in G[node]:
                if child not in visited:
                    visited.add(child)
                    next_layer.add(child)
        current_layer = next_layer
        current_distance += 1

    return current_layer
