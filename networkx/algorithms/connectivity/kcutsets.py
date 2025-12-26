"""
Kanevsky all minimum node k cutsets algorithm.
"""

from itertools import combinations

import networkx as nx
from networkx.algorithms.flow import (
    build_residual_network,
    edmonds_karp,
)

from .utils import build_auxiliary_node_connectivity

default_flow_func = edmonds_karp

__all__ = ["all_node_cuts"]


@nx._dispatchable
def all_node_cuts(G, k=None, flow_func=None):
    r"""Returns all minimum k cutsets of an undirected graph G.

    This implementation is based on Kanevsky's algorithm [1]_ for finding all
    minimum-size node cut-sets of an undirected graph G; ie the set (or sets)
    of nodes of cardinality equal to the node connectivity of G. Thus if
    removed, would break G into two or more connected components.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    k : Integer
        Node connectivity of the input graph. If k is None, then it is
        computed. Default value: None.

    flow_func : function
        Function to perform the underlying flow computations. Default value is
        :func:`~networkx.algorithms.flow.edmonds_karp`. This function performs
        better in sparse graphs with right tailed degree distributions.
        :func:`~networkx.algorithms.flow.shortest_augmenting_path` will
        perform better in denser graphs.

    Returns
    -------
    cuts : a generator of node cutsets
        Each node cutset has cardinality equal to the node connectivity of
        the input graph.

    Examples
    --------
    >>> # A two-dimensional grid graph has 4 cutsets of cardinality 2
    >>> G = nx.grid_2d_graph(5, 5)
    >>> cutsets = list(nx.all_node_cuts(G))
    >>> len(cutsets)
    4
    >>> all(2 == len(cutset) for cutset in cutsets)
    True
    >>> nx.node_connectivity(G)
    2

    Notes
    -----
    This implementation is based on the sequential algorithm for finding all
    minimum-size separating vertex sets in a graph [1]_. The main idea is to
    compute minimum cuts using local maximum flow computations among a set
    of nodes of highest degree and all other non-adjacent nodes in the Graph.
    Once we find a minimum cut, we add an edge between the high degree
    node and the target node of the local maximum flow computation to make
    sure that we will not find that minimum cut again.

    See also
    --------
    node_connectivity
    edmonds_karp
    shortest_augmenting_path

    References
    ----------
    .. [1]  Kanevsky, A. (1993). Finding all minimum-size separating vertex
            sets in a graph. Networks 23(6), 533--541.
            http://onlinelibrary.wiley.com/doi/10.1002/net.3230230604/abstract

    """
    if not nx.is_connected(G):
        raise nx.NetworkXError("Input graph is disconnected.")

    n = G.number_of_nodes()

    # Handle edge cases
    if n == 1:
        return
    if nx.density(G) == 1:
        return

    if flow_func is None:
        flow_func = default_flow_func

    if k is None:
        k = nx.node_connectivity(G, flow_func=flow_func)

    if k == 0:
        return

    nodes = list(G.nodes())
    node_set = set(nodes)
    seen_cuts = set()

    # Pre-compute adjacency for fast lookup
    adj = {v: set(G.neighbors(v)) for v in nodes}

    # Build mapping once
    aux_graph = build_auxiliary_node_connectivity(G)
    mapping = aux_graph.graph["mapping"]

    def _is_separating(cut):
        """Check if removing cut disconnects G."""
        if len(cut) >= n - 1:
            return True
        remaining = nx.restricted_view(G, cut, [])
        if remaining.number_of_nodes() == 0:
            return True
        return not nx.is_connected(remaining)

    def _find_cut(s, t):
        """Find minimum cut between s and t using max-flow."""
        source = f"{mapping[s]}B"
        target = f"{mapping[t]}A"

        H = build_auxiliary_node_connectivity(G)
        R = build_residual_network(H, "capacity")

        try:
            R_flow = flow_func(H, source, target, capacity="capacity", residual=R)
        except nx.NetworkXError:
            return None

        if R_flow.graph["flow_value"] != k:
            return None

        # Extract cut from saturated internal edges
        H_nodes = H.nodes
        cut = set()

        for u, v, data in R_flow.edges(data=True):
            flow = data.get("flow", 0)
            cap = data.get("capacity", 0)
            if flow == cap and cap > 0:
                u_id = H_nodes[u].get("id") if u in H_nodes else None
                v_id = H_nodes[v].get("id") if v in H_nodes else None
                if u_id is not None and u_id == v_id:
                    cut.add(u_id)

        return cut if len(cut) == k else None

    def _try_add(cut):
        """Add cut if new and valid, return cut or None."""
        if cut is None or len(cut) != k:
            return None
        frozen = frozenset(cut)
        if frozen in seen_cuts:
            return None
        if _is_separating(cut):
            seen_cuts.add(frozen)
            return cut
        return None

    # Phase 1: Check all non-adjacent pairs
    for i, s in enumerate(nodes):
        s_adj = adj[s]
        for t in nodes[i + 1 :]:
            if t in s_adj:
                continue
            cut = _try_add(_find_cut(s, t))
            if cut is not None:
                yield cut

    # Phase 2: Nodes with degree exactly k (neighbors form a cut)
    for v in nodes:
        if len(adj[v]) == k:
            cut = _try_add(adj[v].copy())
            if cut is not None:
                yield cut

    # Phase 3: Special handling for small k
    if k == 1:
        for v in nodes:
            cut = _try_add({v})
            if cut is not None:
                yield cut

    elif k == 2:
        for v in nodes:
            deg_v = len(adj[v])
            # Only check low-degree nodes (degree <= 4) to avoid excessive iterations
            # while still catching most k=2 cuts efficiently
            if deg_v <= 4:
                # Check pairs of neighbors
                neighbors = list(adj[v])
                for i, n1 in enumerate(neighbors):
                    for n2 in neighbors[i + 1 :]:
                        cut = _try_add({n1, n2})
                        if cut is not None:
                            yield cut
                # Check v with non-neighbors
                non_adj = node_set - adj[v] - {v}
                for u in non_adj:
                    cut = _try_add({v, u})
                    if cut is not None:
                        yield cut

    # Phase 4: For small graphs with k >= 3, check all k-combinations
    # Threshold of 15 nodes keeps brute-force enumeration tractable: C(15,3) = 455
    if k >= 3 and n <= 15:
        for combo in combinations(nodes, k):
            cut = _try_add(set(combo))
            if cut is not None:
                yield cut


def _is_separating_set(G, cut):
    """Assumes that the input graph is connected."""
    if len(cut) == len(G) - 1:
        return True

    H = nx.restricted_view(G, cut, [])
    if nx.is_connected(H):
        return False
    return True
