"""
Find the (alpha, beta)-cores of a bipartite graph.

The (alpha, beta)-core is found by recursively pruning nodes in the bipartite graph
where the degree of a node in one set is less than alpha,
or the degree of a node in the other set is less than beta.

See the following reference for details:

Efficient (alpha, beta)-core computation: An index-based approach
B. Liu, L. Yuan, X. Lin, L. Qin, W. Zhang, & J. Zhou
The World Wide Web Conference, 2019, pp. 1130-1141.
https://doi.org/10.1145/3308558.3313682
"""

import networkx as nx

__all__ = [
    "alpha_beta_core",
]


@nx._dispatchable
def alpha_beta_core(G, alpha, beta):
    """
    Returns the (alpha, beta)-core of a bipartite graph.

    The (alpha, beta)-core is a maximal subgraph of a bipartite graph where
    each node in one set has at least alpha neighbors in the other set,
    and vice versa.

    Parameters
    ----------
    G : NetworkX graph
        A bipartite graph. The graph must not contain self-loops.
    alpha : int
        The minimum degree requirement for nodes in one partition.
    beta : int
        The minimum degree requirement for nodes in the other partition.

    Returns
    -------
    G : NetworkX graph
        The (alpha, beta)-core subgraph of G.

    Raises
    ------
    NetworkXError
        If the graph is not bipartite or if alpha or beta is less than 1.

    Notes
    -----
    This implementation assumes the input graph is bipartite. It does not
    attempt to verify the bipartite property of the graph beyond its
    partition sets.

    The function iteratively removes nodes that do not satisfy the
    degree constraints in either partition, until the graph stabilizes.

    The input graph, node, and edge attributes are copied to the subgraph.

    Examples
    --------
    >>> import networkx as nx
    >>> B = nx.Graph()
    >>> B.add_edges_from([(1, "a"), (1, "b"), (2, "b"), (2, "c"), (3, "c")])
    >>> G_ab_core = alpha_beta_core(B, alpha=1, beta=2)
    >>> list(G_ab_core.edges)
    [(1, 'b'), (2, 'b'), (2, 'c'), (3, 'c')]

    References
    ----------
    .. [1] Liu, B., Yuan, L., Lin, X., Qin, L., Zhang, W., & Zhou, J. (2019, May).
            Efficient (alpha, beta)-core computation: An index-based approach.
            In The World Wide Web Conference (pp. 1130-1141).
    """
    if not nx.is_bipartite(G):
        raise nx.NetworkXError("Graph is not bipartite")

    if alpha < 1 or beta < 1:
        raise nx.NetworkXError("alpha and beta must be greater than 0")

    U, V = nx.bipartite.sets(G)

    G_tmp = G.copy()

    while True:
        remove_nodes = set()

        for u in U:
            if u in G_tmp and G_tmp.degree(u) < alpha:
                remove_nodes.add(u)

        for v in V:
            if v in G_tmp and G_tmp.degree(v) < beta:
                remove_nodes.add(v)

        if not remove_nodes:
            break

        G_tmp.remove_nodes_from(remove_nodes)

    return G_tmp
