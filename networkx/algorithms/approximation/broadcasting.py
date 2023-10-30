import networkx as nx
from networkx import NetworkXError
from networkx.utils import not_implemented_for

__all__ = [
    "tree_broadcast_center",
    "tree_broadcast_time",
]


def _get_max_broadcast_value(G, U, v, values):
    adj = sorted(set(G.neighbors(v)) & U, key=lambda u: values[u], reverse=True)
    return max(values[u] + i for i, u in enumerate(adj, start=1))


def _get_broadcast_centers(G, v, values, target):
    adj = sorted(set(G.neighbors(v)), key=lambda u: values[u], reverse=True)
    j = min(i for i, u in enumerate(adj, start=1) if values[u] + i == target)
    return set([v] + adj[:j])


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def tree_broadcast_center(G):
    """Return the Broadcast Center of the tree G.

    This is a linear algorithm for determining the broadcast center of any tree with N vertices,
    as a by-product it can also determine the broadcast number of any vertex in the tree.
    The broadcast number of a vertex v in a graph G is the minimum number of time units required to broadcast from v.
    The broadcast center of a graph G is one of the vertices having minimum broadcast number.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph
        The graph should be an undirected tree

    Returns
    -------
    BC : (int, set) tuple
        minimum broadcast number of the tree, set of broadcast centers

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    References
    ----------
    .. [1] Slater, P.J., Cockayne, E.J., Hedetniemi, S.T,
       Information dissemination in trees. SIAM J.Comput. 10(4), 692–701 (1981)
    """
    # Assert that the graph G is a tree
    if not nx.is_tree(G):
        NetworkXError("Your graph is not a tree")
    # step 0
    if G.number_of_nodes() == 2:
        return 1, set(G.nodes())
    elif G.number_of_nodes() == 1:
        return 0, set(G.nodes())

    # step 1
    U = {node for node, deg in G.degree if deg == 1}
    values = {n: 0 for n in U}
    T = G.copy()
    T.remove_nodes_from(U)

    # step 2
    W = {node for node, deg in T.degree if deg == 1}
    values.update((w, G.degree[w] - 1) for w in W)

    # step 3
    while T.number_of_nodes() >= 2:
        # step 4
        w = min(W, key=lambda n: values[n])
        v = next(T.neighbors(w))

        # step 5
        U.add(w)
        W.remove(w)
        T.remove_node(w)

        # step 6
        if T.degree(v) == 1:
            # update t(v)
            values.update({v: _get_max_broadcast_value(G, U, v, values)})
            W.add(v)

    # step 7
    v = nx.utils.arbitrary_element(T)
    b_T = _get_max_broadcast_value(G, U, v, values)
    return b_T, _get_broadcast_centers(G, v, values, b_T)


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def tree_broadcast_time(G, node=None):
    """Return the Broadcast Time of the tree G.

    Broadcasting is an information dissemination problem in which one vertex in a graph, called the originator,
    must distribute a message to all other vertices by placing a series of calls along the edges of the graph.
    Once informed, other vertices aid the originator in distributing the message.
    The broadcasting must be completed as quickly as possible subject to the following constraints:
    - Each call requires one unit of time.
    - A vertex can only participate in one call per unit of time.
    - Each call only involves two adjacent vertices: a sender and a receiver.
    The minimum broadcast time of a vertex is defined as the minimum amount of time required to complete
    broadcasting starting from the originator.
    The broadcast time of a graph is defined as the maximum broadcast time from all its vertices.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph
        The graph should be an undirected tree
    node: int
        index of starting vertex. If none,
        the algorithm returns the broadcast
        time of the tree.
    Returns
    -------
    BT : int
        Broadcast Time of a vertex in a tree

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    References
    ----------
    .. [1] Slater, P.J., Cockayne, E.J., Hedetniemi, S.T,
       Information dissemination in trees. SIAM J.Comput. 10(4), 692–701 (1981)
    """
    b_T, b_C = tree_broadcast_center(G)
    if node is None:
        return b_T + max(nx.eccentricity(G, b_C).values())
    else:
        b_T, b_C = tree_broadcast_center(G)
        return b_T + max(nx.eccentricity(G, b_C).values())
