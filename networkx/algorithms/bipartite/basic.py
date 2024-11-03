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
        or non-bipartite graphs. Note that when enabled, some adjacent
        nodes may have the same color, resulting in a non-strict
        bipartite coloring. This is useful for graphs that are "almost"
        bipartite or when analyzing disconnected components separately.

    Returns
    -------
    Dict[node, int]
        A dictionary keyed by node with a 1 or 0 as data for each node color.
        When relaxed=True, the coloring may not strictly satisfy bipartite
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

    >>> # Example with relaxed coloring on a non-bipartite graph
    >>> G = nx.cycle_graph(3)  # Odd cycle, not bipartite
    >>> color = nx.bipartite.color(G, relaxed=True)  # Won't raise error
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
def is_bipartite(G: nx.Graph, relaxed: bool = False) -> bool:
    """Returns True if graph G is bipartite, False if not.

    Parameters
    ----------
    G : NetworkX graph
        The graph to check for bipartite properties.
    relaxed : bool, default=False
        If True, allows checking bipartiteness for disconnected components
        separately. In relaxed mode, a graph with some bipartite and some
        non-bipartite components will return True for the bipartite components.

    Returns
    -------
    bool
        True if the graph is bipartite, False otherwise.
        When relaxed=True, returns True if at least one component is bipartite.

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
        Container of nodes to check if they form one set of a bipartite
        partition. Must contain all nodes of one part of the bipartite
        graph without duplicates.

    Returns
    -------
    bool
        True if the nodes form a valid bipartite set, False otherwise.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> X = {1, 3}
    >>> bipartite.is_bipartite_node_set(G, X)
    True

    Notes
    -----
    - Raises an exception if the input nodes contain duplicates, as this
      would lead to incorrect results in bipartite algorithms.
    - For connected graphs, the bipartite sets are unique.
    - This function handles disconnected graphs correctly.
    """
    S = set(nodes)

    if len(S) < len(nodes):
        raise AmbiguousSolution(
            "The input node set contains duplicates.\n"
            "This may lead to incorrect results when using it in bipartite algorithms.\n"
            "Consider using set(nodes) as the input"
        )

    for CC in (G.subgraph(c).copy() for c in connected_components(G)):
        X, Y = sets(CC)
        if not (
            (X.issubset(S) and Y.isdisjoint(S)) or (Y.issubset(S) and X.isdisjoint(S))
        ):
            return False
    return True


@nx._dispatchable
def sets(
    G: nx.Graph, top_nodes: Optional[Container] = None, relaxed: bool = False
) -> Tuple[Set, Set]:
    """Returns bipartite node sets of graph G.

    Parameters
    ----------
    G : NetworkX graph
        The graph to partition into bipartite sets.
    top_nodes : Container, optional
        Container with all nodes in one bipartite node set. If not supplied,
        it will be computed. For disconnected graphs, this helps resolve
        ambiguity in the bipartition.
    relaxed : bool, default=False
        If True, allows partial bipartite sets for disconnected components.
        This is useful when some components are bipartite while others
        are not. Note that enabling this may result in non-optimal
        partitioning for non-bipartite components.

    Returns
    -------
    Tuple[Set, Set]
        A tuple containing two sets (X, Y) representing the bipartite partition.
        When relaxed=True, the sets may not form a perfect bipartition for
        all components.

    Raises
    ------
    AmbiguousSolution
        Raised if the input bipartite graph is disconnected and no container
        with all nodes in one bipartite set is provided. This is because
        multiple valid solutions exist for disconnected graphs.
    NetworkXError
        Raised if the input graph is not bipartite and relaxed=False.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms import bipartite
    >>> G = nx.path_graph(4)
    >>> X, Y = bipartite.sets(G)
    >>> list(X)
    [0, 2]
    >>> list(Y)
    [1, 3]

    See Also
    --------
    color : Returns a two-coloring of the graph
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
def density(B: nx.Graph, nodes: Container) -> float:
    """Returns density of bipartite graph B.

    The density of a bipartite graph is defined as the ratio of the number
    of edges present to the maximum possible number of edges between the
    two node sets.

    Parameters
    ----------
    B : NetworkX graph
        The bipartite graph to calculate density for.
    nodes : Container
        Container of nodes in one bipartite node set. Must contain all nodes
        from exactly one of the two sets in the bipartite graph. This is
        required to properly calculate the maximum possible edges between
        the two sets.

    Returns
    -------
    float
        The bipartite density value, between 0.0 and 1.0 inclusive.
        - 0.0 means no edges between the sets
        - 1.0 means every possible edge exists between the sets

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> X = {0, 1, 2}  # One of the node sets
    >>> bipartite.density(G, X)
    1.0

    Notes
    -----
    - The nodes container must contain all nodes from exactly one of the
      two bipartite sets to avoid ambiguity with disconnected graphs.
    - For directed graphs, the density is calculated considering edges
      in both directions.
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
def degrees(
    B: nx.Graph, nodes: Container, weight: Optional[str] = None
) -> Tuple[Dict[Any, Union[int, float]], Dict[Any, Union[int, float]]]:
    """Returns the degrees of the two node sets in the bipartite graph B.

    Parameters
    ----------
    B : NetworkX graph
        The bipartite graph to calculate degrees for.
    nodes : Container
        Container with all nodes from one bipartite node set. Must contain
        all nodes from exactly one of the two sets to properly separate
        the degree calculations.
    weight : str, optional
        The edge attribute that holds the numerical value used as a weight.
        If None, then each edge has weight 1. The degree is the sum of the
        edge weights adjacent to the node.

    Returns
    -------
    Tuple[Dict[node, Union[int, float]], Dict[node, Union[int, float]]]
        A tuple of two dictionaries containing the degrees of nodes in each
        set. The first dictionary contains degrees for nodes not in the
        input set, and the second contains degrees for nodes in the input
        set.

    Examples
    --------
    >>> import networkx as nx
    >>> from networkx.algorithms import bipartite
    >>> G = nx.complete_bipartite_graph(3, 2)
    >>> Y = {3, 4}  # One of the node sets
    >>> degX, degY = bipartite.degrees(G, Y)
    >>> dict(degX)  # Degrees of nodes in the other set
    {0: 2, 1: 2, 2: 2}

    Notes
    -----
    - The nodes container must contain all nodes from exactly one of the
      two bipartite sets to avoid ambiguity with disconnected graphs.
    - For weighted graphs, the degrees will be the sum of the edge weights
      connected to each node.
    """
    bottom = set(nodes)
    top = set(B) - bottom
    return (B.degree(top, weight), B.degree(bottom, weight))