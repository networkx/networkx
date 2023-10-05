import networkx as nx
from networkx import NetworkXError
from networkx.utils import not_implemented_for

__all__ = [
    "tree_broadcast_time",
]


def _get_max_broadcast_value(G, U, v, values):
    adj = sorted(set(G.neighbors(v)) & U, key=lambda u: values[u], reverse=True)
    return max(values[u] + i for i, u in enumerate(adj, start=1))


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def tree_broadcast_time(G):
    """Return the optimal Broadcast Time of the tree G.

    Broadcasting is an information dissemination problem in which one vertex in a graph, called the originator,
    must distribute a message to all other vertices by placing a series of calls along the edges of the graph.
    Once informed, other vertices aid the originator in distributing the message. This is assumed to take place
    in discrete time units.
    The optimal broadcast time of a tree is defined as the minimum amount of time required to complete
    broadcasting starting from the originator.
    This function implements a linear algorithm for determining the minimum broadcast
    time on any undirected tree [1]_.

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph
        The graph should be an undirected tree

    Returns
    -------
    b_T : int
        Optimal Broadcast Time of a tree

    Raises
    ------
    NetworkXNotImplemented
        If the graph is directed or is a multigraph.

    References
    ----------
    .. [1] Slater, P.J., Cockayne, E.J., Hedetniemi, S.T,
       Information dissemination in trees. SIAM J.Comput. 10(4), 692–701 (1981)
    """
    # Remove selfloops if necessary
    loop_nodes = nx.nodes_with_selfloops(G)
    try:
        node = next(loop_nodes)
    except StopIteration:
        pass
    else:
        G = G.copy()
        G.remove_edge(node, node)
        G.remove_edges_from((n, n) for n in loop_nodes)

    # Assert that the graph G has no cycles
    if not nx.is_tree(G):
        NetworkXError("Your graph is not a tree")
    # step 0
    if G.number_of_nodes() == 2:
        return 1
    elif G.number_of_nodes() == 1:
        return 0

    # step 1
    U = {node for node, deg in G.degree if deg == 1}
    values = {n: 0 for n in U}
    T = G.copy()
    T.remove_nodes_from(U)

    # step 2
    values.update((node, deg -1) for node, deg in T.degree if deg = 1)

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
    return b_T
