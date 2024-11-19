"""
==========================
Bipartite Graph Algorithms
==========================
"""

import networkx as nx
from networkx.algorithms.components import connected_components
from networkx.exception import AmbiguousSolution

__all__ = [
    "is_bipartite",
    "is_bipartite_node_set",
    "color",
    "sets",
    "density",
    "degrees",
]


@nx._dispatchable
def color(G, relaxed=False):
    """Returns a two-coloring of the graph.

    Raises an exception if the graph is not bipartite and relaxed=False.

    Parameters
    ----------
    G : NetworkX graph
        The graph to be colored.
    relaxed : bool, default=False
        If True, allows a partial bicoloring for disconnected components
        or non-bipartite graphs.

    Returns
    -------
    color : dictionary
        A dictionary keyed by node with a 1 or 0 as data for each node color.

    Raises
    ------
    NetworkXError
        If the graph is not two-colorable and relaxed=False.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> c = bipartite.color(G)
    >>> print(c)
    {0: 1, 1: 0, 2: 1, 3: 0}

    You can use this to set a node attribute indicating the bipartite set:

    >>> nx.set_node_attributes(G, c, "bipartite")
    >>> print(G.nodes[0]["bipartite"])
    1
    >>> print(G.nodes[1]["bipartite"])
    0

    Notes
    -----
    In directed graphs, in-neighbors and out-neighbors are both considered for coloring.
    """

    if G.is_directed():
        import itertools

        def neighbors(v):
            return itertools.chain.from_iterable([G.predecessors(v), G.successors(v)])
    else:
        neighbors = G.neighbors

    color = {}
    for n in G:  # handle disconnected graphs
        if n in color or len(G[n]) == 0:  # skip isolates
            continue
        queue = [n]
        color[n] = 1  # nodes seen with color (1 or 0)
        while queue:
            v = queue.pop()
            c = 1 - color[v]  # opposite color of node v
            for w in neighbors(v):
                if w in color:
                    if color[w] == color[v] and not relaxed:
                        raise nx.NetworkXError("Graph is not bipartite.")
                else:
                    color[w] = c
                    queue.append(w)
    # color isolates with 0
    color.update(dict.fromkeys(nx.isolates(G), 0))
    return color


@nx._dispatchable
def is_bipartite(G, relaxed=False):
    """Returns True if graph G is bipartite, False if not.

    Parameters
    ----------
    G : NetworkX graph
    relaxed : bool, default=False
        If True, considers disconnected graphs and non-bipartite components.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> print(bipartite.is_bipartite(G))
    True
    """
    try:
        color(G, relaxed=relaxed)
        return True
    except nx.NetworkXError:
        return False


@nx._dispatchable
def is_bipartite_node_set(G, nodes):
    """Returns True if nodes and G/nodes are a bipartition of G.

    Parameters
    ----------
    G : NetworkX graph
    nodes: list or container
      Check if nodes are a one of a bipartite set.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> X = set([1, 3])
    >>> bipartite.is_bipartite_node_set(G, X)
    True
    """
    S = set(nodes)
    if len(S) < len(nodes):
        raise AmbiguousSolution(
            "The input node set contains duplicates.\n"
            "Consider using set(nodes) as the input"
        )

    for CC in (G.subgraph(c).copy() for c in connected_components(G)):
        X, Y = sets(CC)
        if not ((X.issubset(S) and Y.isdisjoint(S)) or (Y.issubset(S) and X.isdisjoint(S))):
            return False
    return True


@nx._dispatchable
def sets(G, top_nodes=None, relaxed=False):
    """Returns bipartite node sets of graph G.

    Parameters
    ----------
    G : NetworkX graph
    top_nodes : container, optional
        Container with all nodes in one bipartite node set.
    relaxed : bool, default=False
        If True, handles disconnected graphs and non-bipartite components.

    Returns
    -------
    X, Y : set, set
        Sets of nodes that are separated by the bipartite edge set.

    Raises
    ------
    AmbiguousSolution
        If the graph is disconnected and no container with all nodes in one
        bipartite set is provided, unless relaxed=True.
    NetworkXError
        If the graph is not bipartite and relaxed=False.

    Notes
    -----
    If the graph is not bipartite and `relaxed=False`, an error is raised even if some components are bipartite.
    """
    if G.is_directed():
        is_connected = nx.is_weakly_connected
    else:
        is_connected = nx.is_connected

    if top_nodes is not None:
        X = set(top_nodes)
        Y = set(G) - X
    else:
        if not is_connected(G) and not relaxed:
            msg = (
                "Disconnected graph: Ambiguous solution for bipartite sets. "
                "Either provide top_nodes or use relaxed=True."
            )
            raise nx.AmbiguousSolution(msg)
        c = color(G, relaxed=relaxed)
        X = {n for n, is_top in c.items() if is_top}
        Y = {n for n, is_top in c.items() if not is_top}
    return (X, Y)


@nx._dispatchable(graphs="B")
def density(B, nodes):
    """Returns density of bipartite graph B.

    Parameters
    ----------
    B : NetworkX graph
    nodes: list or container
      Nodes in one node set of the bipartite graph.

    Returns
    -------
    d : float
       The bipartite density

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> X = set([0, 1, 2])
    >>> bipartite.density(G, X)
    1.0
    """
    n = len(B)
    m = nx.number_of_edges(B)
    nb = len(nodes)
    nt = n - nb
    if m == 0:  # includes cases n==0 and n==1
        d = 0.0
    else:
        if B.is_directed():
            d = m / (2 * nb * nt)
        else:
            d = m / (nb * nt)
    return d


@nx._dispatchable(graphs="B", edge_attrs="weight")
def degrees(B, nodes, weight=None):
    """Returns the degrees of the two node sets in the bipartite graph B.

    Parameters
    ----------
    B : NetworkX graph
    nodes: list or container
      Nodes in one node set of the bipartite graph.
    weight : string or None, optional (default=None)
       The edge attribute that holds the numerical value used as a weight.
       If None, then each edge has weight 1.

    Returns
    -------
    (degX,degY) : tuple of dictionaries
       The degrees of the two bipartite sets as dictionaries keyed by node.

    Examples
    --------
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> Y = set([3, 4])
    >>> degX, degY = bipartite.degrees(G, Y)
    >>> dict(degX)
    {0: 2, 1: 2, 2: 2}

     Notes
    -----
    For multi-graphs, degrees are computed as the sum of weights or counts across parallel edges.
    """
    bottom = set(nodes)
    top = set(B) - bottom
    return (B.degree(top, weight), B.degree(bottom, weight))