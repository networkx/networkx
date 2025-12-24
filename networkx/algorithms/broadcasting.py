"""Routines to calculate the broadcast time of certain graphs.

Broadcasting is an information dissemination problem in which a node in a graph,
called the originator, must distribute a message to all other nodes by placing
a series of calls along the edges of the graph. Once informed, other nodes aid
the originator in distributing the message.

The broadcasting must be completed as quickly as possible subject to the
following constraints:
- Each call requires one unit of time.
- A node can only participate in one call per unit of time.
- Each call only involves two adjacent nodes: a sender and a receiver.
"""

import warnings

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "tree_broadcast_center",
    "tree_broadcast_time",
]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def tree_broadcast_center(G):
    """Return the broadcast center of a tree.

    .. deprecated:: 3.6
       tree_broadcast_center is deprecated and will be removed in NetworkX 3.8.
       Use ``nx.tree.broadcast_center`` instead.

    The broadcast center of a graph `G` denotes the set of nodes having
    minimum broadcast time [1]_. This function implements a linear algorithm
    for determining the broadcast center of a tree with ``n`` nodes. As a
    by-product, it also determines the broadcast time from the broadcast center.

    Parameters
    ----------
    G : Graph
        The graph should be an undirected tree.

    Returns
    -------
    b_T, b_C : (int, set) tuple
        Minimum broadcast time of the broadcast center in `G`, set of nodes
        in the broadcast center.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed or is a multigraph.

    NotATree
        If `G` is not a tree.

    References
    ----------
    .. [1] Slater, P.J., Cockayne, E.J., Hedetniemi, S.T,
       Information dissemination in trees. SIAM J.Comput. 10(4), 692–701 (1981)
    """
    warnings.warn(
        "tree_broadcast_center is deprecated and will be removed in NetworkX 3.8.\n"
        "Use `nx.tree.broadcast_center` instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    if not nx.is_tree(G):
        raise nx.NotATree("G is not a tree")
    return nx.tree.broadcast_center(G)


@not_implemented_for("directed")
@not_implemented_for("multigraph")
@nx._dispatchable
def tree_broadcast_time(G, node=None):
    """Return the minimum broadcast time of a (node in a) tree.

    .. deprecated:: 3.6
       tree_broadcast_time is deprecated and will be removed in NetworkX 3.8.
       Use ``nx.tree.broadcast_time`` instead.

    The minimum broadcast time of a node is defined as the minimum amount
    of time required to complete broadcasting starting from that node.
    The broadcast time of a graph is the maximum over
    all nodes of the minimum broadcast time from that node [1]_.
    This function returns the minimum broadcast time of `node`.
    If `node` is `None`, the broadcast time for the graph is returned.

    Parameters
    ----------
    G : Graph
        The graph should be an undirected tree.

    node : node, optional (default=None)
        Starting node for the broadcasting. If `None`, the algorithm
        returns the broadcast time of the graph instead.

    Returns
    -------
    int
        Minimum broadcast time of `node` in `G`, or broadcast time of `G`
        if no node is provided.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed or is a multigraph.

    NodeNotFound
        If `node` is not a node in `G`.

    NotATree
        If `G` is not a tree.

    References
    ----------
    .. [1] Harutyunyan, H. A. and Li, Z.
        "A Simple Construction of Broadcast Graphs."
        In Computing and Combinatorics. COCOON 2019
        (Ed. D. Z. Du and C. Tian.) Springer, pp. 240-253, 2019.
    """
    warnings.warn(
        "tree_broadcast_time is deprecated and will be removed in NetworkX 3.8.\n"
        "Use `nx.tree.broadcast_time` instead.",
        category=DeprecationWarning,
        stacklevel=2,
    )
    if not nx.is_tree(G):
        raise nx.NotATree("G is not a tree")
    return nx.tree.broadcast_time(G, node=node)
