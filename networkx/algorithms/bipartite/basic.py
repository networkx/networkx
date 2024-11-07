"""
==========================
Bipartite Graph Algorithms
==========================
"""

from typing import Dict, Set, Tuple, Optional, Container, Union, Any
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
def color(G: nx.Graph, relaxed: bool = False) -> Dict[Any, int]:
    """Returns a two-coloring of the graph.

    Parameters
    ----------
    G : NetworkX graph
        The graph to be colored.
    relaxed : bool, default=False
        If True, allows a partial bicoloring for disconnected components
        or non-bipartite graphs. When enabled, some adjacent nodes may
        have the same color, resulting in a non-strict bipartite coloring.
        This is useful for "almost" bipartite graphs or when analyzing
        disconnected components separately.

    Returns
    -------
    Dict[node, int]
        A dictionary keyed by node with a color (1 or 0) assigned to each node.
        When `relaxed=True`, the coloring may not strictly satisfy bipartite
        properties.

    Raises
    ------
    NetworkXError
        If the graph is not two-colorable and `relaxed` is False.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> color = nx.bipartite.color(G)
    >>> color
    {0: 1, 1: 0, 2: 1, 3: 0}
    """
    neighbors = G.predecessors if G.is_directed() else G.neighbors

    color = {}
    for n in G:
        if n in color or len(G[n]) == 0:  # skip isolates
            continue
        queue = [n]
        color[n] = 1
        while queue:
            v = queue.pop()
            c = 1 - color[v]  # opposite color
            for w in neighbors(v):
                if w in color:
                    if color[w] == color[v] and not relaxed:
                        raise nx.NetworkXError("Graph is not bipartite.")
                else:
                    color[w] = c
                    queue.append(w)
    color.update(dict.fromkeys(nx.isolates(G), 0))
    return color


@nx._dispatchable
def is_bipartite(G: nx.Graph, relaxed: bool = False) -> bool:
    """Returns True if graph G is bipartite, False otherwise.

    Parameters
    ----------
    G : NetworkX graph
        The graph to check.
    relaxed : bool, default=False
        If True, allows checking bipartiteness for disconnected components
        separately.

    Returns
    -------
    bool
        True if the graph is bipartite, False otherwise.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> nx.bipartite.is_bipartite(G)
    True
    """
    try:
        color(G, relaxed=relaxed)
        return True
    except nx.NetworkXError:
        return False


@nx._dispatchable
def is_bipartite_node_set(G: nx.Graph, nodes: Container) -> bool:
    """Returns True if nodes and G/nodes are a bipartition of G.

    Parameters
    ----------
    G : NetworkX graph
        The graph to check for bipartition.
    nodes : Container
        A container of nodes to check for a valid bipartition.

    Returns
    -------
    bool
        True if the nodes form a valid bipartite set, False otherwise.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> X = {1, 3}
    >>> bipartite.is_bipartite_node_set(G, X)
    True
    """
    S = set(nodes)

    if len(S) < len(nodes):
        raise AmbiguousSolution("The input node set contains duplicates.")

    for CC in (G.subgraph(c).copy() for c in connected_components(G)):
        X, Y = sets(CC)
        if not ((X.issubset(S) and Y.isdisjoint(S)) or (Y.issubset(S) and X.isdisjoint(S))):
            return False
    return True


@nx._dispatchable
def sets(G: nx.Graph, top_nodes: Optional[Container] = None, relaxed: bool = False) -> Tuple[Set, Set]:
    """Returns bipartite node sets of graph G.

    Parameters
    ----------
    G : NetworkX graph
        The graph to partition.
    top_nodes : Container, optional
        A container with all nodes in one bipartite node set.
    relaxed : bool, default=False
        Allows partial bipartite sets for disconnected components.

    Returns
    -------
    Tuple[Set, Set]
        A tuple containing two sets (X, Y) representing the bipartite partition.

    Raises
    ------
    AmbiguousSolution
        Raised if the input bipartite graph is disconnected without `top_nodes`.

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.path_graph(4)
    >>> X, Y = bipartite.sets(G)
    """
    if top_nodes is not None:
        X, Y = set(top_nodes), set(G) - set(top_nodes)
    else:
        if not (nx.is_weakly_connected if G.is_directed() else nx.is_connected)(G) and not relaxed:
            raise nx.AmbiguousSolution(
                "Disconnected graph: Provide `top_nodes` or set `relaxed=True`."
            )
        coloring = color(G, relaxed=relaxed)
        X, Y = {n for n, is_top in coloring.items() if is_top}, {n for n, is_top in coloring.items() if not is_top}
    return X, Y


@nx._dispatchable
def density(B: nx.Graph, nodes: Container) -> float:
    """Returns density of bipartite graph B.

    Parameters
    ----------
    B : NetworkX graph
        The bipartite graph.
    nodes : Container
        Container of nodes in one bipartite set.

    Returns
    -------
    float
        Density value, between 0.0 and 1.0 inclusive.

    Examples
    --------
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> X = {0, 1, 2}
    >>> bipartite.density(G, X)
    1.0
    """
    n, m, nb = len(B), nx.number_of_edges(B), len(nodes)
    nt = n - nb
    return m / (2 * nb * nt) if B.is_directed() else m / (nb * nt)


@nx._dispatchable
def degrees(B: nx.Graph, nodes: Container, weight: Optional[str] = None) -> Tuple[Dict[Any, Union[int, float]], Dict[Any, Union[int, float]]]:
    """Returns degrees of the two node sets in the bipartite graph B.

    Parameters
    ----------
    B : NetworkX graph
        The bipartite graph.
    nodes : Container
        A container with all nodes from one bipartite set.
    weight : str, optional
        The edge attribute to use as weight.

    Returns
    -------
    Tuple[Dict[node, Union[int, float]], Dict[node, Union[int, float]]]
        A tuple of two dictionaries containing the degrees of nodes in each set.

    Examples
    --------
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> Y = {3, 4}
    >>> degX, degY = bipartite.degrees(G, Y)
    """
    bottom, top = set(nodes), set(B) - set(nodes)
    return B.degree(top, weight), B.degree(bottom, weight)
