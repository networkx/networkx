from collections import deque
from itertools import chain

import networkx as nx
from networkx.utils import not_implemented_for, pairwise

__all__ = ["metric_closure", "steiner_tree", "directed_steiner_tree"]


@not_implemented_for("directed")
@nx._dispatchable(edge_attrs="weight", returns_graph=True)
def metric_closure(G, weight="weight"):
    """Return the metric closure of a graph.

    The metric closure of a graph *G* is the complete graph in which each edge
    is weighted by the shortest path distance between the nodes in *G* .

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    NetworkX graph
        Metric closure of the graph `G`.

    """
    M = nx.Graph()

    Gnodes = set(G)

    # check for connected graph while processing first node
    all_paths_iter = nx.all_pairs_dijkstra(G, weight=weight)
    u, (distance, path) = next(all_paths_iter)
    if len(G) != len(distance):
        msg = "G is not a connected graph. metric_closure is not defined."
        raise nx.NetworkXError(msg)
    Gnodes.remove(u)
    for v in Gnodes:
        M.add_edge(u, v, distance=distance[v], path=path[v])

    # first node done -- now process the rest
    for u, (distance, path) in all_paths_iter:
        Gnodes.remove(u)
        for v in Gnodes:
            M.add_edge(u, v, distance=distance[v], path=path[v])

    return M


def _mehlhorn_steiner_tree(G, terminal_nodes, weight):
    distances, paths = nx.multi_source_dijkstra(G, terminal_nodes, weight=weight)

    d_1 = {}
    s = {}
    for v in G.nodes():
        s[v] = paths[v][0]
        d_1[(v, s[v])] = distances[v]

    # G1-G4 names match those from the Mehlhorn 1988 paper.
    G_1_prime = nx.Graph()
    # iterate over all edges to complete d1
    for u, v, data in G.edges(data=True):
        su, sv = s[u], s[v]
        weight_here = d_1[(u, su)] + data.get(weight, 1) + d_1[(v, sv)]
        if not G_1_prime.has_edge(su, sv):
            G_1_prime.add_edge(su, sv, weight_d1=weight_here)
        else:
            new_weight = min(weight_here, G_1_prime[su][sv]["weight_d1"])
            G_1_prime.add_edge(su, sv, weight_d1=new_weight)

    G_2 = nx.minimum_spanning_edges(G_1_prime, data=True, weight="weight_d1")

    G_3 = nx.Graph()
    for u, v, _ in G_2:
        path = nx.shortest_path(G, u, v, weight=weight)
        for n1, n2 in pairwise(path):
            G_3.add_edge(n1, n2, weight=G[n1][n2].get(weight, 1))

    G_3_mst = list(nx.minimum_spanning_edges(G_3, data=False, weight=weight))
    if G.is_multigraph():
        G_3_mst = (
            (u, v, min(G[u][v], key=lambda k: G[u][v][k].get(weight, 1)))
            for u, v in G_3_mst
        )
    G_4 = G.edge_subgraph(G_3_mst).copy()
    _remove_nonterminal_leaves(G_4, terminal_nodes)
    return G_4.edges()


def _kou_steiner_tree(G, terminal_nodes, weight):
    # Compute the metric closure only for terminal nodes
    # Create a complete graph H from the metric edges
    H = nx.Graph()
    unvisited_terminals = set(terminal_nodes)

    # check for connected graph while processing first node
    u = unvisited_terminals.pop()
    distances, paths = nx.single_source_dijkstra(G, source=u, weight=weight)
    if len(G) != len(distances):
        msg = "G is not a connected graph."
        raise nx.NetworkXError(msg)
    for v in unvisited_terminals:
        H.add_edge(u, v, distance=distances[v], path=paths[v])

    # first node done -- now process the rest
    for u in unvisited_terminals.copy():
        distances, paths = nx.single_source_dijkstra(G, source=u, weight=weight)
        unvisited_terminals.remove(u)
        for v in unvisited_terminals:
            H.add_edge(u, v, distance=distances[v], path=paths[v])

    # Use the 'distance' attribute of each edge provided by H.
    mst_edges = nx.minimum_spanning_edges(H, weight="distance", data=True)

    # Create an iterator over each edge in each shortest path; repeats are okay
    mst_all_edges = chain.from_iterable(pairwise(d["path"]) for u, v, d in mst_edges)
    if G.is_multigraph():
        mst_all_edges = (
            (u, v, min(G[u][v], key=lambda k: G[u][v][k].get(weight, 1)))
            for u, v in mst_all_edges
        )

    # Find the MST again, over this new set of edges
    G_S = G.edge_subgraph(mst_all_edges)
    T_S = nx.minimum_spanning_edges(G_S, weight="weight", data=False)

    # Leaf nodes that are not terminal might still remain; remove them here
    T_H = G.edge_subgraph(T_S).copy()
    _remove_nonterminal_leaves(T_H, terminal_nodes)

    return T_H.edges()


def _remove_nonterminal_leaves(G, terminals):
    terminal_set = set(terminals)
    leaves = {n for n in G if len(set(G[n]) - {n}) == 1}
    nonterminal_leaves = leaves - terminal_set

    while nonterminal_leaves:
        # Removing a node may create new non-terminal leaves, so we limit
        # search for candidate non-terminal nodes to neighbors of current
        # non-terminal nodes
        candidate_leaves = set.union(*(set(G[n]) for n in nonterminal_leaves))
        candidate_leaves -= nonterminal_leaves | terminal_set
        # Remove current set of non-terminal nodes
        G.remove_nodes_from(nonterminal_leaves)
        # Find any new non-terminal nodes from the set of candidates
        leaves = {n for n in candidate_leaves if len(set(G[n]) - {n}) == 1}
        nonterminal_leaves = leaves - terminal_set


ALGORITHMS = {
    "kou": _kou_steiner_tree,
    "mehlhorn": _mehlhorn_steiner_tree,
}


@not_implemented_for("directed")
@nx._dispatchable(preserve_all_attrs=True, returns_graph=True)
def steiner_tree(G, terminal_nodes, weight="weight", method=None):
    r"""Return an approximation to the minimum Steiner tree of a graph.

    The minimum Steiner tree of `G` w.r.t a set of `terminal_nodes` (also *S*)
    is a tree within `G` that spans those nodes and has minimum size (sum of
    edge weights) among all such trees.

    The approximation algorithm is specified with the `method` keyword
    argument. All three available algorithms produce a tree whose weight is
    within a ``(2 - (2 / l))`` factor of the weight of the optimal Steiner tree,
    where ``l`` is the minimum number of leaf nodes across all possible Steiner
    trees.

    * ``"kou"`` [2]_ (runtime $O(|S| |V|^2)$) computes the minimum spanning tree of
      the subgraph of the metric closure of *G* induced by the terminal nodes,
      where the metric closure of *G* is the complete graph in which each edge is
      weighted by the shortest path distance between the nodes in *G*.

    * ``"mehlhorn"`` [3]_ (runtime $O(|E|+|V|\log|V|)$) modifies Kou et al.'s
      algorithm, beginning by finding the closest terminal node for each
      non-terminal. This data is used to create a complete graph containing only
      the terminal nodes, in which edge is weighted with the shortest path
      distance between them. The algorithm then proceeds in the same way as Kou
      et al..

    Parameters
    ----------
    G : NetworkX graph

    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    weight : string (default = 'weight')
        Use the edge attribute specified by this string as the edge weight.
        Any edge attribute not present defaults to 1.

    method : string, optional (default = 'mehlhorn')
        The algorithm to use to approximate the Steiner tree.
        Supported options: 'kou', 'mehlhorn'.
        Other inputs produce a ValueError.

    Returns
    -------
    NetworkX graph
        Approximation to the minimum steiner tree of `G` induced by
        `terminal_nodes` .

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed.

    ValueError
        If the specified `method` is not supported.

    Notes
    -----
    For multigraphs, the edge between two nodes with minimum weight is the
    edge put into the Steiner tree.


    References
    ----------
    .. [1] Steiner_tree_problem on Wikipedia.
           https://en.wikipedia.org/wiki/Steiner_tree_problem
    .. [2] Kou, L., G. Markowsky, and L. Berman. 1981.
           ‘A Fast Algorithm for Steiner Trees’.
           Acta Informatica 15 (2): 141–45.
           https://doi.org/10.1007/BF00288961.
    .. [3] Mehlhorn, Kurt. 1988.
           ‘A Faster Approximation Algorithm for the Steiner Problem in Graphs’.
           Information Processing Letters 27 (3): 125–28.
           https://doi.org/10.1016/0020-0190(88)90066-X.
    """
    if method is None:
        method = "mehlhorn"

    try:
        algo = ALGORITHMS[method]
    except KeyError as e:
        raise ValueError(f"{method} is not a valid choice for an algorithm.") from e

    edges = algo(G, terminal_nodes, weight)
    # For multigraph we should add the minimal weight edge keys
    if G.is_multigraph():
        edges = (
            (u, v, min(G[u][v], key=lambda k: G[u][v][k][weight])) for u, v in edges
        )
    T = G.edge_subgraph(edges)
    return T


def _reachable_within(G, source, cutoff):
    """Return the set of nodes reachable from source within cutoff depth."""
    seen = {source}
    q = deque([(source, 0)])
    while q:
        node, depth = q.popleft()
        if depth == cutoff:
            continue
        for nbr in G[node]:
            if nbr not in seen:
                seen.add(nbr)
                q.append((nbr, depth + 1))
    return seen


def _directed_steiner_tree_density(G, terminals, weight):
    """Compute density = total cost / #covered terminals."""
    if G.number_of_edges() == 0:
        return float("inf")

    terminals = set(terminals)
    num_terminals = 0
    total = 0
    for u, v, d in G.edges(data=True):
        if u in terminals:
            terminals.remove(u)
            num_terminals += 1
        if v in terminals:
            terminals.remove(v)
            num_terminals += 1
        total += d.get(weight, 1)

    return float("inf") if num_terminals == 0 else total / num_terminals


def _directed_steiner_tree(G, root, terminals, min_terminals, cutoff, weight):
    """Recursive helper for directed_steiner_tree."""
    H = nx.DiGraph()
    if min_terminals <= 0 or not terminals or cutoff == 0:
        return H

    terminals = set(terminals)
    if cutoff == 1:
        H.add_node(root, **G.nodes[root])
        edges_filtered = [
            (u, v, d) for u, v, d in G.edges(data=True) if u == root and v in terminals
        ]

        for u, v, d in edges_filtered:
            H.add_node(v, **G.nodes[v])
            H.add_edge(u, v, **d)

        return H

    reached_terminals = set()
    while len(reached_terminals) < min_terminals and terminals:
        min_sub_tree = nx.DiGraph()
        min_density = float("inf")

        for v in G.successors(root):
            for n in range(1, len(terminals) + 1):
                sub_tree = _directed_steiner_tree(
                    G, v, terminals, n, cutoff - 1, weight
                )
                sub_tree.add_node(root, **G.nodes[root])
                sub_tree.add_node(v, **G.nodes[v])
                sub_tree.add_edge(root, v, **G[root][v])

                sub_density = _directed_steiner_tree_density(
                    sub_tree, terminals, weight
                )
                if sub_density < min_density:
                    min_sub_tree = sub_tree
                    min_density = sub_density
        covered_terminals = {n for n in min_sub_tree.nodes if n in terminals}
        if not covered_terminals:
            return H
        reached_terminals |= covered_terminals
        terminals -= reached_terminals

        H.add_nodes_from(min_sub_tree.nodes(data=True))
        H.add_edges_from(min_sub_tree.edges(data=True))

    return H


def directed_steiner_tree(
    G, root, terminals, min_terminals=None, cutoff=None, weight="weight"
):
    """Approximation algorithm for the Directed Steiner Tree problem.

    Parameters
    ----------
    G : DiGraph
        A directed graph.
    root : node
        The root node.
    terminals : set
        Set of terminal nodes to be connected.
    min_terminals : int
        Minimum number of terminals to connect.
    cutoff : int, optional
        Maximum search depth from the root.
    weight : string, optional (default="weight")
        Edge attribute to use as weight.

    Returns
    -------
    H : DiGraph
        A directed Steiner tree subgraph.

    Raises
    ------
    NetworkXError
        If ``G`` is not directed, if root is not in ``G``, if cutoff
        is not a positive integer or None, if ``min_terminals`` is
        not a positive integer, if ``min_terminals`` exceeds the
        number of given terminals, if ``min_terminals`` is not
        a positive integer or if any terminals are not in ``G``.
    NetworkXUnfeasible
        If no terminals are given, if no terminals are reachable from
        the root within the cutoff, or if the resulting tree fails
        to cover at least ``min_terminals`` terminals.

    References
    ----------
    .. [1] Charikar, M., Chekuri, C., Cheung, T-Y., Dai, Z., Goel, A.,
           Guha, S., & Li, M. (1999). Approximation algorithms for
           directed Steiner problems. *Journal of Algorithms*, 33(1), 73–91.
           https://doi.org/10.1006/jagm.1999.1042
    """
    if not G.is_directed():
        raise nx.NetworkXError("directed_steiner_tree only works for directed graphs")

    if root not in G:
        raise nx.NetworkXError(f"Root {root} not in G")

    terminals = set(terminals)
    if not terminals:
        raise nx.NetworkXUnfeasible("No terminals given")

    if cutoff is None:
        cutoff = float("inf")
    elif cutoff <= 0:
        raise nx.NetworkXError("cutoff must be a positive integer or None")

    if min_terminals is None:
        min_terminals = len(terminals)
    elif min_terminals <= 0:
        raise nx.NetworkXError("min_terminals must be a positive integer or None")
    elif min_terminals > len(terminals):
        raise nx.NetworkXError(
            "min_terminals must be less than or equal to the number of terminals"
        )

    missing = terminals - set(G.nodes)
    if missing:
        raise nx.NetworkXError(f"Terminals {missing} not in G")

    reachable_terminals = terminals & _reachable_within(G, root, cutoff)
    if not reachable_terminals:
        raise nx.NetworkXUnfeasible(
            f"No terminals are reachable from root {root} within cutoff={cutoff}"
        )

    H = _directed_steiner_tree(
        G, root, reachable_terminals, min_terminals, cutoff, weight
    )
    covered = set(H.nodes) & set(reachable_terminals)
    if len(covered) < min_terminals:
        raise nx.NetworkXUnfeasible(
            f"Directed Steiner tree could not cover at least {min_terminals} terminals {list(reachable_terminals)}"
        )
    return H
