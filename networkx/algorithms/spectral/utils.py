"""
Utility classes and functions for cut finding algorithms.
"""

import networkx as nx
from networkx.utils import py_random_state

__all__ = [
    "generate_random_orthogonal_gaussian",
    "build_flow_network",
    "flow_matching",
    "compute_mincut",
    "build_subdivision_graph",
]

py_random_state("_seed")


def generate_random_orthogonal_gaussian(dim, quantity, _seed=None):
    """Generate `quantity` many random Gaussian unit vectors of dimension `dim` which
    are all orthogonal to the all ones vector.

    Parameters
    ----------
    dim : int
        The dimension of the returned vectors.

    quantity : int
        The number of vectors to generate.

    _seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    np.array
        A numpy array of shape (dim, quantity) such that each column is a random
        gaussian vector orthogonal to the all ones vector.
    """
    import numpy as np

    if dim == 1:
        return np.full((1, quantity), 0)

    vecs = _seed.normal(size=(quantity, dim))
    vecs = vecs - (vecs @ np.full((dim, 1), 1 / dim))
    vecs = vecs.T
    col_norms = np.linalg.norm(vecs, axis=0)
    return vecs / col_norms


def build_flow_network(G, _s, _t, S, T=None, c=1, d=1):
    """Builds a flow network on `G` where each edge has capacity `c`, and each node of `S`, `T`
    have a supply / demand of d respectively.

    Parameters
    ----------
    G : networkx.Graph

    _s : object
        The key for the super-source node which will be added to the flow network. Must
        satisify `_s not in G`.

    _t : object
        The key for the super-sink node which will be added to the flow network. Must
        satisfy `_t not in G`.

    S : collection
        A collection of nodes in `G`.

    T : collection
        A collection of nodes in `G`. If not specified, defaults to the complement of `S`.

    c : int
        The capacity of each edge of `G` in the flow network.

    d : int
        The supply of nodes in `S` and demand of nodes in `T`.

    Returns
    -------
    networkx.Graph
        A graph such that each node `v in S` has supply `d`, and each node `u in T` has
        demand `d`, and each edge of `G` has capacity `c`.

    Raises
    ------
    NetworkXError
        if `_s` or `_t` is already in `G`, if edge capacities are negative,
        or if nodes have negative demand.
    """
    if _s in G or _t in G:
        raise nx.NetworkXError(
            "The keys _s and _t for the super-source and"
            "super-sink must satisfy `_s not in G` and `_t not in G`."
        )
    if c < 0:
        raise nx.NetworkXError("Edges must have non-negative capacity.")
    if d < 0:
        raise nx.NetworkXError("Nodes must have non-negative demand.")

    H = G.__class__()
    H.add_nodes_from(G.nodes)
    H.add_edges_from(G.edges, capacity=c)
    for v in G:
        if v in S:
            H.add_edge(_s, v, capacity=d)
        elif T and v in T:
            H.add_edge(_t, v, capacity=d)
        elif not T:
            H.add_edge(_t, v, capacity=d)
    return H


def extract_path(parents, s, t):
    """Using the DFS tree, find a path between s and t."""
    u = parents[t]
    path = [(u, t)]
    while u is not s:
        path.append((parents[u], u))
        u = parents[u]
    return path


def dfs(R, s, t):
    """DFS to find an s-t path in the residual graph R, using only edges with
    positive flow.
    """
    visited = set()
    parents = {}
    stack = []
    stack.append((s, R.neighbors(s)))

    while stack:
        try:
            u, u_nbrs = stack[-1]
            v = next(u_nbrs)
        except StopIteration:
            stack.pop()
            continue

        if R[u][v]["flow"] <= 0 or v in visited:
            continue
        else:
            visited.add(v)
            parents[v] = u
            stack.append((v, R.neighbors(v)))
        if v is t:
            return extract_path(parents, s, t)
    return []


def flow_matching(R, _s, _t):
    """Given a residual network `R` on which a flow problem has been solved, a super-source `_s`,
    and a super-sink `_t`, decompose the flow into `_s` - `_t` and find a matching between
    nodes adjacent to `_s` and nodes adjacent to `_t`.

    Parameters
    ----------
    R : NetworkX DiGraph
        A residual network on which a flow problem has been solved. Must have the edge attribute
        `flow`

    _s : object
        The key of the super-source node in `R`.

    _t : object
        The key of the super-sink node in `R`

    Returns
    -------
    dict
        A matching between nodes adjacennt to `_s` and nodes adjacent to `_t`
    """
    matching = {}
    path = dfs(R, _s, _t)
    while path:
        s = path[0][0]
        t = path[-1][1]
        matching[s] = t
        matching[t] = s
        for u, v in path:
            R[u][v]["flow"] -= 1
            if R[u][v]["flow"] <= 0:
                R.remove_edge(u, v)
        path = dfs(R, _s, _t)
    return matching


def compute_mincut(R, _t):
    """Computes the min-cut in R. Always returns the smaller side of the cut first."""
    cutset = [(u, v, d) for u, v, d in R.edges(data=True) if d["flow"] == d["capacity"]]
    R.remove_edges_from(cutset)

    non_reachable = set(nx.shortest_path_length(R, target=_t))
    partition = (non_reachable, set(R) - non_reachable)
    if len(non_reachable) >= len(R) // 2:
        partition = (set(R) - non_reachable, non_reachable)
    R.add_edges_from(cutset)
    return partition


def build_subdivision_graph(G, subdiv_node_format=None):
    """Builds the subdivision graph of `G`, where the subdivision node of an edge
    (u, v) is given the key subdiv_node_format(u, v).

    Parameters
    ----------
    G : NetworkX Graph

    subdidv_node_format : function
        Takes two arguments u, v and returns the key for the subdivision node of the edge (u, v).
        If not specified, the default key is f"{str(u)} - {str(v)}".

    Returns
    -------
    H : NetworkX Graph
        A graph where each edge (u, v) of `G` is replaced by a node subdiv_node_format(u, v)
        and the edges are (u, subdiv_node_format(u, v)), (subdiv_node_format(u, v), v).

    subdiv_nodes : collection
        A collection of the subdivision nodes that were added

    Raises
    ------
    NetworkXError
        If the function subdiv_node_format is specified and not callable.
    """
    if not subdiv_node_format:

        def default_subdiv_format(u, v):
            return f"{str(u)} - {str(v)}"

        subdiv_node_format = default_subdiv_format
    if not callable(subdiv_node_format):
        raise nx.NetworkXError("subdiv_node_format must be callable")
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    subdiv_nodes = set()
    for u, v in G.edges():
        subdivision_vertex = subdiv_node_format(u, v)
        H.add_edge(u, subdivision_vertex)
        H.add_edge(subdivision_vertex, v)
        subdiv_nodes.add(subdivision_vertex)
    return H, subdiv_nodes
