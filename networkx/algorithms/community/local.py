"""
Local Community Detection Algorithms

Local Community Detection (LCD) aims to detected one or a few communities sarting from certain source nodes in the network. This differs from Global Communty Detection (GCD), which aims to partition an entire network into communities.

LCD is often useful when only a portion of the know graph is known or the graph is large enough that GCD is infeasable

[1]_ Gives a good introduction and overview of LCD see this review here

References
----------
.. [1] Baltsou, Georgia, Konstantinos Christopoulos, and Konstantinos Tsichlas.
Local community detection: A survey. IEEE Access 10 (2022): 110701-110726.
https://doi.org/10.1109/ACCESS.2022.3213980

"""

__all__ = ["clauset"]


def clauset(G, source, cutoff=None):
    """Find the local community around a source node using the Greedy Source
    Expansion algorithm.

    Clausets algorithm [1]_ uses freedy source expansion to identify a local community starting from a given source node and expanding it based on the local modularity gain at each step. The algorithm adds neighboring nodes that maximize local modularity to the community iteratively, stopping when no additional nodes improve the modularity or when a predefined cutoff is reached.

    Local modularity measures the density of edges within a community relative to the total graph. By focusing on local modularity, the algorithm efficiently uncovers communities around a specific node without requiring global optimization over the entire graph.

    The algorithm assumes that the graph $G$ consists of a known community $C$ and an unknown set of nodes $U$, which are adjacent to $C$ . The boundary of the community $B$, consists of nodes in $C$ that have at least one neighbor in $U$.

    Mathematically, the local modularity is expressed as:

    .. math::
        R = \frac{I}{T}

    where $T$ is the number of edges with on or more endpoitns in $B$, and $I$ is the number of those edges with neither endpoint in $U$.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    source : node
        The source node from which the community expansion begins.

    cutoff : int, optional (default=None)
        The maximum number of nodes to include in the community. If None, the algorithm expands until no further modularity gain can be made.

    Returns
    ----------
    set
        A set of nodes representing the local community around the source node.

    Examples
    ----------
    >>> G = nx.karate_club_graph()
    >>> nx.community.clauset(G, source=16)
    {0, 4, 5, 6, 10, 11, 16}

    Notes
    -----
    This algorithm is designed for detecting local communities around a specific node, which is useful for large networks where global community detection is computationally expensive. The method follows the local modularity optimization framework introduced by Clauset [1]_.

    The result of the algorithm may vary based on the structure of the graph, the choice of the source node, and the presence of ties between nodes during the greedy expansion process.

    References
    ----------
    .. [1] Clauset, Aaron. Finding local community structure in networks.
    Physical Review E—Statistical, Nonlinear, and Soft Matter Physics 72, no. 2 (2005): 026132.
    https://arxiv.org/pdf/physics/0503036

    """
    if cutoff is None:
        cutoff = float("inf")
    C = {source}
    U = set(G.neighbors(source)) - C
    R_value = 0
    while len(C) < cutoff:
        if len(U) == 0:
            break
        max_R = 0
        best_node = None
        for v in U:
            C_tmp = C | {v}
            B_tmp = {
                node
                for node in C_tmp
                for neighbor in G.neighbors(node)
                if neighbor in U - {v}
            }
            T_tmp = {
                frozenset([node, neighbor])
                for node in B_tmp
                for neighbor in G.neighbors(node)
            }
            I_tmp = {edge for edge in T_tmp if all(node in C_tmp for node in edge)}
            R_tmp = len(I_tmp) / len(T_tmp) if len(T_tmp) > 0 else 1

            if R_tmp > max_R:
                max_R = R_tmp
                best_node = v

        C = C | {best_node}
        U.update(set(G.neighbors(best_node)) - C - U)
        U.remove(best_node)
        if max_R < R_value:
            break
        R_value = max_R

    return C
