"""
==========================
Bipartite Graph Algorithms
==========================
"""

from networkx.algorithms.components import connected_components
from networkx.exception import AmbiguousSolution
import networkx as nx

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

    Parameters
    ----------
    G : NetworkX graph
        The graph to be colored.
    relaxed : bool, default=False
        If True, allows a partial bicoloring for disconnected components
        or non-bipartite graphs.

    Returns
    -------
    dict
        A dictionary keyed by node with a 1 or 0 as data for each node color.

    Raises
    ------
    NetworkXError
        If the graph is not two-colorable and relaxed is False.
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
    """Returns True if graph G is bipartite, False if not."""
    try:
        color(G, relaxed=relaxed)
        return True
    except nx.NetworkXError:
        return False

@nx._dispatchable
def is_bipartite_node_set(G, nodes):
    """Returns True if nodes and G/nodes are a bipartition of G."""
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
    """Returns bipartite node sets of graph G."""
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

@nx._dispatchable
def density(B, nodes):
    """Returns density of bipartite graph B."""
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

@nx._dispatchable
def degrees(B, nodes, weight=None):
    """Returns the degrees of the two node sets in the bipartite graph B."""
    bottom = set(nodes)
    top = set(B) - bottom
    return (B.degree(top, weight), B.degree(bottom, weight))