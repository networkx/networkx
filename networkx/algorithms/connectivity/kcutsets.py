"""
Kanevsky all minimum node k cutsets algorithm.
"""

from collections import defaultdict
from operator import itemgetter

import networkx as nx
from networkx.algorithms.approximation.connectivity import (
    local_node_connectivity as approx_local_node_connectivity,
)
from networkx.algorithms.flow import (
    build_residual_network,
    edmonds_karp,
    shortest_augmenting_path,
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

    Before each of those maximum flow computations a much cheaper call is
    made to the shortest path based approximation of local node
    connectivity (see
    :meth:`networkx.algorithms.approximation.local_node_connectivity`),
    following [2]_. Only a pair of nodes whose local node connectivity is
    exactly $k$ can yield a cut of cardinality $k$, and the approximation
    is a strict lower bound on that connectivity, so a pair for which it
    already exceeds $k$ is skipped. This does not change the cuts that are
    returned, nor the order in which they are generated.

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

    .. [2]  Robert S. Sinkovits. Fast and Accurate Determination of Graph Node
            Connectivity Leveraging Approximate Methods. Computational Science
            - ICCS 2021, Lecture Notes in Computer Science, Volume 12742,
            Springer, 2021.
            https://doi.org/10.1007/978-3-030-77961-0_41

    """
    if not nx.is_connected(G):
        raise nx.NetworkXError("Input graph is disconnected.")

    # Address some corner cases first.
    # For complete Graphs
    if nx.density(G) == 1:
        yield from ()
        return

    # Initialize data structures.
    # Keep track of the cuts already computed so we do not repeat them.
    seen = []
    # Even-Tarjan reduction is what we call auxiliary digraph
    # for node connectivity.
    H = build_auxiliary_node_connectivity(G)
    H_nodes = H.nodes  # for speed
    mapping = H.graph["mapping"]
    # The Even-Tarjan reduction requires infinite capacity on external
    # edges (edges between different original nodes) and capacity 1 on
    # internal edges (vA -> vB). build_auxiliary_node_connectivity sets
    # capacity=1 on all edges, which is sufficient for computing the
    # node connectivity value but not for Kanevsky's algorithm, which
    # depends on the residual graph structure.
    for u, w, d in H.edges(data=True):
        if H_nodes[u]["id"] != H_nodes[w]["id"]:
            d["capacity"] = float("inf")
    R = build_residual_network(H, "capacity")
    kwargs = {"capacity": "capacity", "residual": R}
    # Define default flow function
    if flow_func is None:
        flow_func = default_flow_func
    if flow_func is shortest_augmenting_path:
        kwargs["two_phase"] = True
    # Begin the actual algorithm
    # step 1: Find node connectivity k of G
    if k is None:
        k = nx.node_connectivity(G, flow_func=flow_func)
    # step 2:
    # Find k nodes with top degree, call it X:
    X = {n for n, d in sorted(G.degree(), key=itemgetter(1), reverse=True)[:k]}
    # Check if X is a k-node-cutset
    if _is_separating_set(G, X):
        seen.append(X)
        yield X

    for x in X:
        # step 3: Compute local connectivity flow of x with all other
        # non adjacent nodes in G
        non_adjacent = set(G) - {x} - set(G[x])
        for v in non_adjacent:
            # Only a pair whose local node connectivity is exactly k can
            # contribute a cut of cardinality k. The shortest path based
            # approximation is a strict lower bound on that connectivity,
            # so a value above k proves this pair cannot, and the maximum
            # flow below is a waste. Skipping the pair is not merely safe
            # but invisible: everything the loop does past this point,
            # including the bookkeeping edge added to H and R, happens
            # only when the flow value equals k.
            if approx_local_node_connectivity(G, x, v, cutoff=k + 1) > k:
                continue
            # step 4: compute maximum flow in an Even-Tarjan reduction H of G
            # and step 5: build the associated residual network R
            # After adding edges in previous iterations, there may be
            # infinite-capacity paths between x and v, which means no
            # finite min-cut exists for this pair. Skip in that case.
            try:
                R = flow_func(H, f"{mapping[x]}B", f"{mapping[v]}A", **kwargs)
            except nx.NetworkXUnbounded:
                continue
            flow_value = R.graph["flow_value"]

            if flow_value == k:
                # Remove edges with zero residual capacity from R.
                # Residual capacity = capacity - flow.
                # For saturated forward edges: cap == flow > 0 -> removed.
                # For inactive reverse edges: cap == flow == 0 -> removed.
                # For active reverse edges: cap=0, flow < 0 -> cap != flow
                #   -> kept (these have positive residual capacity and
                #   represent cancellable flow in the residual graph).
                saturated_edges = [
                    (u, w, d)
                    for (u, w, d) in R.edges(data=True)
                    if d["capacity"] == d["flow"]
                ]
                R.remove_edges_from(saturated_edges)
                # step 6: shrink the strongly connected components of
                # residual flow network R and call it L.
                L = nx.condensation(R)
                cmap = L.graph["mapping"]
                inv_cmap = defaultdict(list)
                for n, scc in cmap.items():
                    inv_cmap[scc].append(n)
                # Compute the transitive closure of L for successor lookups.
                # Per Picard-Queyranne, each antichain of L corresponds to
                # a successor-closed set (the antichain plus all successors),
                # which defines the source side of a minimum s-t cut.
                L_closure = nx.transitive_closure(L)
                # step 7: Compute all antichains of L;
                # they map to closed sets in H.
                for antichain in nx.antichains(L):
                    if not antichain:
                        continue
                    # Build the successor-closed set in L from the antichain.
                    S_L = set(antichain)
                    for scc_node in antichain:
                        S_L.update(L_closure[scc_node])
                    # Expand SCC nodes back to R/H nodes.
                    S = set()
                    for scc_node in S_L:
                        S.update(inv_cmap[scc_node])
                    # S must contain the source and not the sink.
                    if f"{mapping[x]}B" not in S or f"{mapping[v]}A" in S:
                        continue
                    # Find the cutset: edges from S to ~S in H.
                    cutset = set()
                    for u in S:
                        cutset.update((u, w) for w in H[u] if w not in S)
                    if not cutset:
                        continue
                    node_cut = {H_nodes[u]["id"] for u, _ in cutset}

                    if node_cut not in seen:
                        yield node_cut
                        seen.append(node_cut)

                # Add an edge (x, v) to make sure that we do not
                # find this cutset again. This is equivalent
                # of adding the edge in the input graph
                # G.add_edge(x, v) and then regenerate H and R:
                # Add edges to the auxiliary digraph.
                # External edges get infinite capacity.
                H.add_edge(f"{mapping[x]}B", f"{mapping[v]}A", capacity=float("inf"))
                H.add_edge(f"{mapping[v]}B", f"{mapping[x]}A", capacity=float("inf"))
                # Add edges to the residual network.
                # See build_residual_network for convention we used
                # in residual graphs.
                R.add_edge(f"{mapping[x]}B", f"{mapping[v]}A", capacity=R.graph["inf"])
                R.add_edge(f"{mapping[v]}A", f"{mapping[x]}B", capacity=0)
                R.add_edge(f"{mapping[v]}B", f"{mapping[x]}A", capacity=R.graph["inf"])
                R.add_edge(f"{mapping[x]}A", f"{mapping[v]}B", capacity=0)

                # Add again the saturated edges to reuse the residual network
                R.add_edges_from(saturated_edges)


def _is_separating_set(G, cut):
    """Assumes that the input graph is connected"""
    if len(cut) == len(G) - 1:
        return True

    H = nx.restricted_view(G, cut, [])
    if nx.is_connected(H):
        return False
    return True
