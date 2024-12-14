"""Functions for finding connected dominating sets.

A `dominating set`_ for an undirected graph *G* with vertex set *V*
and edge set *E* is a subset *D* of *V* such that every vertex not in
*D* is adjacent to at least one member of *D*. A `connected dominating set`_
is a dominating set *C* that induces a connected subgraph of *G*.

.. _dominating set: https://en.wikipedia.org/wiki/Domintaing_set
.. _connected dominating set: https://en.wikipedia.org/wiki/Connected_dominating_set

"""

from heapq import heappop, heappush

import networkx as nx

from ..utils import not_implemented_for

__all__ = [
    "guha_khuller_pair_scan_connected_dominating_set",
    "guha_khuller_black_components_connected_dominating_set",
]


@not_implemented_for("directed")
@nx._dispachable
def guha_khuller_pair_scan_connected_dominating_set(G):
    r"""Returns a connected dominating set.

    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_.
 
    Parameters
    ----------
    G : NewtorkX graph
        Undirected graph.

    Returns
    -------
    black_nodes : set
        Returns a dominating set of nodes which induce a connected subgraph of G.

    Examples
    --------
    >>> G = nx.Graph([ \
        (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), \
        (2, 7), (3, 8), (4, 9), (5, 10), (6, 11), \
        (7, 12), (8, 12), (9, 12), (10, 12), (11, 12) \
    ])
    >>> nx.guha_khuller_pair_scan_connected_dominating_set(G)
    {1, 2, 12, 7}

    Raises
    ------
    NetworkXNotImplemented
        If G is directed.

    Notes
    -----
    This algorithm yields a connected dominating set of size at most
    :math:`2(1 + H(\Delta)) \cdot \lvert OPT_{DS} \rvert`,
    where :math:`\Delta` is the maximum degree, :math:`H` is the
    harmonic functin and :math:`OPT_{DS}` is an optimal dominating set in the graph.
    Runtime of the algorithm is $O(|V||E|)$.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set
    .. [3] Guha, S. and Khuller, S.
           *Approximation Algorithms for Connected Dominating Sets*.
           Algorithmica, 20, 374-387, 1998.

    """
    G_succ = G._adj  # For speed-up

    # Some renaming for convenience
    push = heappush
    pop = heappop

    # Find node with highest degree
    max_deg_node = max(G, key=G.degree)

    # Track node colors
    colors = {v: "wt" for v in G}
    colors[max_deg_node] = "gr"

    # Keep sets of white and gray neighbors for each node
    wt_nbrs = {v: {u for u in G.neighbors(v) if u != max_deg_node} for v in G}

    gr_nbrs = {
        v: {max_deg_node} if v in G.neighbors(max_deg_node) else set() for v in G
    }

    # Max-heap of white nodes adjacent to gray nodes
    frontier = []

    # The yield of a pair of nodes is size of the union
    # of their white neighbors sets
    def _pair_yield(u, v):
        return len(wt_nbrs[u] | wt_nbrs[v])

    def _single_yield(v):
        return len(wt_nbrs[v])

    # Initialize frontier
    for nbr in wt_nbrs[max_deg_node]:
        push(frontier, (-_pair_yield(max_deg_node, nbr), (max_deg_node, nbr)))

    while frontier:
        (neg_deg, (gr_node, wt_node)) = pop(frontier)

        # Check if yield decreased while in the heap
        pair_yield = _pair_yield(gr_node, wt_node)
        if -neg_deg > pair_yield:
            push(frontier, (-pair_yield, (gr_node, wt_node)))
            continue

        if colors[gr_node] != "gr" or colors[wt_node] != "wt":
            continue

        # Check for best yield of a single gray node
        cur_gray_nodes = [v for v, color in colors.items() if color == "gr"]
        max_yield_node = max(cur_gray_nodes, key=_single_yield)
        max_yield = _single_yield(max_yield_node)

        # Only scan a pair if its yield is at least twice that of the
        # gray node with highest yield
        if pair_yield < 2 * max_yield:
            colors[max_yield_node] = "bk"

            for nbr in gr_nbrs[max_yield_node] | wt_nbrs[max_yield_node]:
                gr_nbrs[nbr].remove(max_yield_node)

            new_gray_nodes = wt_nbrs[max_yield_node]
        else:
            colors[gr_node] = "bk"
            colors[wt_node] = "bk"

            gr_nbrs[wt_node].remove(gr_node)
            wt_nbrs[gr_node].remove(wt_node)

            for nbr in gr_nbrs[gr_node] | wt_nbrs[gr_node]:
                gr_nbrs[nbr].remove(gr_node)

            for nbr in gr_nbrs[wt_node] | wt_nbrs[wt_node]:
                wt_nbrs[nbr].remove(wt_node)

            new_gray_nodes = wt_nbrs[gr_node] | wt_nbrs[wt_node]

        # Update nbrs of new gray nodes
        for node in new_gray_nodes:
            colors[node] = "gr"
            for nbr in wt_nbrs[node] | gr_nbrs[node]:
                wt_nbrs[nbr].remove(node)
                gr_nbrs[nbr].add(node)

        for node in new_gray_nodes:
            for nbr in wt_nbrs[node]:
                push(frontier, (-_pair_yield(node, nbr), (node, nbr)))

    black_nodes = {v for v in colors if colors[v] == "bk"}
    return black_nodes


@not_implemented_for("directed")
def guha_khuller_black_components_connected_dominating_set(G):
    r"""Returns a connected dominating set.
 
    A *dominating set* for a graph *G* with node set *V* is a subset *D* of
    *V* such that every node not in *D* is adjacent to at least one
    member of *D* [1]_. A *connected dominating set* is a dominating
    set *C* that induces a connected subgraph of *G* [2]_.

    Parameters
    ----------
    G : NewtorkX graph
        Undirected graph.

    Returns
    -------
    black_nodes : set
        Returns a dominating set of nodes which induce a connected subgraph of G.

    Examples
    --------
    >>> G = nx.Graph([ \
        (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), \
        (2, 7), (3, 8), (4, 9), (5, 10), (6, 11), \
        (7, 12), (8, 12), (9, 12), (10, 12), (11, 12) \
    ])
    >>> nx.guha_khuller_black_components_connected_dominating_set(G)
    {8, 1, 3, 12}

    Raises
    ------
    NetworkXNotImplemented
        If G is directed.

    Notes
    -----
    This algorithm yields a connected dominating set of size at most
    :math:`(\ln \Delta + 3) \cdot \lvert OPT_{CDS} \rvert`,
    where :math:`\Delta` is the maximum degree and :math:`OPT_{CDS}`
    is an optimal connected dominating set in the graph.

    References
    ----------
    .. [1] https://en.wikipedia.org/wiki/Dominating_set
    .. [2] https://en.wikipedia.org/wiki/Connected_dominating_set
    .. [3] Guha, S. and Khuller, S.
           *Approximation Algorithms for Connected Dominating Sets*.
           Algorithmica, 20, 374-387, 1998.
    
    """

    #############################
    ######     Phase I     ######
    #############################
    colors = {v: "wt" for v in G}

    wt_nbrs = {v: set(G.neighbors(v)) for v in G}
    gr_nbrs = {v: set() for v in G}
    bk_nbrs = {v: set() for v in G}

    ################    Disjoint set    ##################

    # Disjoint set dictionary
    bk_comps = {}

    # Create a set containing only v
    def _make_set(v):
        bk_comps[v] = {"parent": v, "rank": 0}

    # Return the set representative of v
    # Perform path compression on the way up
    def _find_set(v):
        parent = bk_comps[v]["parent"]
        if v != parent:
            bk_comps[v]["parent"] = _find_set(parent)
        return bk_comps[v]["parent"]

    # Union by rank
    def __link(u, v):
        if bk_comps[u]["rank"] > bk_comps[v]["rank"]:
            bk_comps[v]["parent"] = u
        else:
            bk_comps[u]["parent"] = v
            if bk_comps[u]["rank"] == bk_comps[v]["rank"]:
                bk_comps[v]["rank"] += 1

    def _union(u, v):
        __link(_find_set(u), _find_set(v))

    ######################################################

    # Comparison criterion for choosing the next black node
    def _reduction(v):
        if colors[v] == "wt":
            return len(wt_nbrs[v])
        else:
            # v is gray, find the number of distinct black components
            # adjacent to it
            comps = {_find_set(u) for u in bk_nbrs[v]}

        return len(wt_nbrs[v]) + len(comps) - 1

    # Update black components
    def _update_bk_comps(v):
        _make_set(v)
        for u in bk_nbrs[v]:
            _union(u, v)

    # Auxiliary function for updating the nbrs of a soon-to-become-black node v
    def _update_nbrs(v):
        # Move v to the black nbrs set for all of v's nbrs
        if colors[v] == "wt":
            color_dict = wt_nbrs
        else:
            color_dict = gr_nbrs

        for nbr in G.neighbors(v):
            color_dict[nbr].remove(v)
            bk_nbrs[nbr].add(v)

        # Color v's white nbrs gray
        # Copy the set to avoid changing it while iterating over it
        v_wt_nbrs = set(wt_nbrs[v])
        for nbr in v_wt_nbrs:
            colors[nbr] = "gr"
            # Move the new gray node to the gray nbrs set for all its nbrs
            for nnbr in G.neighbors(nbr):
                wt_nbrs[nnbr].remove(nbr)
                gr_nbrs[nnbr].add(nbr)

    # Main loop
    candidates = set(G)
    while candidates:
        v = max(candidates, key=_reduction)
        if _reduction(v) == 0:
            break
        candidates.remove(v)
        _update_bk_comps(v)
        _update_nbrs(v)
        colors[v] = "bk"

    #############################
    #####     Phase II      #####
    #############################

    def _find_gr_node_rep(v):
        assert bk_nbrs[v]
        bk_nbr = bk_nbrs[v].pop()
        bk_nbrs[v].add(bk_nbr)
        rep = _find_set(bk_nbr)
        return rep

    def _add_gr_node_to_comp(v, v_rep):
        colors[v] = "bk"
        _make_set(v)
        _union(v, v_rep)

    # Number of black components
    n_bk_comps = len({s["parent"] for s in bk_comps.values()})

    # Gray nodes to consider for connecting black components
    gray_nodes = {v for v, c in colors.items() if c == "gr"}

    # Create the set of all edges connecting two gray vertices,
    # each adjacent to a different black component
    gray_edges = set()

    for v in gray_nodes:
        for nbr in gr_nbrs[v]:
            if (v, nbr) not in gray_edges and (nbr, v) not in gray_edges:
                gray_edges.add((v, nbr))

    for v, u in gray_edges:
        v_rep = _find_gr_node_rep(v)
        u_rep = _find_gr_node_rep(u)
        if v_rep != u_rep:
            if colors[v] == "gr":
                _add_gr_node_to_comp(v, v_rep)
            if colors[u] == "gr":
                _add_gr_node_to_comp(u, u_rep)
            _union(v, u)

    black_nodes = {v for v, c in colors.items() if c == "bk"}
    return black_nodes
