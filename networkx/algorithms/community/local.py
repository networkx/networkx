"""
Local Community Detection Algorithms

Local Community Detection (LCD) aims to detected one or a few communities
starting from certain source nodes in the network. This differs from Global
Communty Detection (GCD), which aims to partition an entire network into
communities.

LCD is often useful when only a portion of the graph is known or the
graph is large enough that GCD is infeasable

[1]_ Gives a good introduction and overview of LCD

References
----------
.. [1] Baltsou, Georgia, Konstantinos Christopoulos, and Konstantinos Tsichlas.
   Local community detection: A survey. IEEE Access 10 (2022): 110701-110726.
   https://doi.org/10.1109/ACCESS.2022.3213980


"""

__all__ = ["clauset_greedy_source_expansion"]


def clauset_greedy_source_expansion(G, *, source, cutoff=None):
    r"""Find the local community around a source node.

    Find the local community around a source node using the Greedy Source
    Expansion algorithm as described by Clauset [1]_. The algorithm identifies a
    local community starting from the source node and expands it based on the
    local modularity gain at each step. The algorithm adds neighboring nodes
    that maximize local modularity to the community iteratively, stopping when
    no additional nodes improve the modularity or when a predefined cutoff is
    reached.

    Local modularity measures the density of edges within a community relative
    to the total graph. By focusing on local modularity, the algorithm efficiently
    uncovers communities around a specific node without requiring global
    optimization over the entire graph.

    The algorithm assumes that the graph $G$ consists of a known community $C$ and
    an unknown set of nodes $U$, which are adjacent to $C$ . The boundary of the
    community $B$, consists of nodes in $C$ that have at least one neighbor in $U$.

    Mathematically, the local modularity is expressed as:

    .. math::
        R = \frac{I}{T}

    where $T$ is the number of edges with one or more endpoints in $B$, and $I$ is the
    number of those edges with neither endpoint in $U$.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.

    source : node
        The source node from which the community expansion begins.

    cutoff : int, optional (default=None)
        The maximum number of nodes to include in the community. If None, the algorithm
        expands until no further modularity gain can be made.

    Returns
    -------
    set
        A set of nodes representing the local community around the source node.

    Examples
    ----------
    >>> G = nx.karate_club_graph()
    >>> nx.community.clauset_greedy_source_expansion(G, source=16)
    {16, 0, 4, 5, 6, 10}

    Notes
    -----
    This algorithm is designed for detecting local communities around a specific node,
    which is useful for large networks where global community detection is computationally
    expensive. The method follows the local modularity optimization framework introduced
    by Clauset [1]_.

    The result of the algorithm may vary based on the structure of the graph, the choice of
    the source node, and the presence of ties between nodes during the greedy expansion process.

    References
    ----------
    .. [1] Clauset, Aaron. Finding local community structure in networks.
      Physical Review E—Statistical, Nonlinear, and Soft Matter Physics 72, no. 2 (2005): 026132.
      https://arxiv.org/pdf/physics/0503036

    """
    if cutoff is None:
        cutoff = float("inf")
    C = {source}
    B = {source}
    U = G[source].keys() - C
    T = {frozenset([node, neighbor]) for node in B for neighbor in G.neighbors(node)}
    I = {edge for edge in T if all(node in C for node in edge)}

    R_value = 0
    while len(C) < cutoff:
        if not U:
            break

        max_R = 0
        best_node = None
        best_node_B = best_node_T = best_node_I = set()

        for v in U:
            R_tmp, B_tmp, T_tmp, I_tmp = _calculate_local_modularity_for_candidate(
                G, v, C, B, T, I
            )
            if R_tmp > max_R:
                max_R = R_tmp
                best_node = v
                best_node_B = B_tmp
                best_node_T = T_tmp
                best_node_I = I_tmp

        C = C | {best_node}
        U.update(G[best_node].keys() - C)
        U.remove(best_node)
        B = best_node_B
        T = best_node_T
        I = best_node_I
        if max_R < R_value:
            break
        R_value = max_R

    return C


def _calculate_local_modularity_for_candidate(G, v, C, B, T, I):
    """
    Compute the local modularity R and updated variables when adding node v to the community.

    Parameters
    ----------
    G : NetworkX graph
        The input graph.
    v : node
        The candidate node to add to the community.
    C : set
        The current set of community nodes.
    B : set
        The current set of boundary nodes.
    T : set of frozenset
        The current set of boundary edges.
    I : set of frozenset
        The current set of internal boundary edges.

    Returns
    -------
    R_tmp : float
        The local modularity after adding node v.
    B_tmp : set
        The updated set of boundary nodes.
    T_tmp : set of frozenset
        The updated set of boundary edges.
    I_tmp : set of frozenset
        The updated set of internal boundary edges.
    """
    C_tmp = C | {v}
    B_tmp = B.copy()
    T_tmp = T.copy()
    I_tmp = I.copy()
    removed_B_nodes = set()

    # Update boundary nodes and edges
    for neighbour in G[v]:
        if neighbour not in C_tmp:
            # v has neighbors not in the community, so it remains a boundary node
            B_tmp.add(v)
            # Add edge between v and neighbor to boundary edges
            T_tmp.add(frozenset([v, neighbour]))

        if neighbour in B:
            # Check if neighbor should be removed from boundary nodes
            neighour_still_in_B = False
            # Go through neighbours neighbours to see if it is still a boundary node
            for neighbours_neighbour in G[neighbour]:
                if neighbours_neighbour not in C_tmp:
                    neighour_still_in_B = True
                    break
            if not neighour_still_in_B:
                B_tmp.remove(neighbour)
                removed_B_nodes.add(neighbour)

        if neighbour in C_tmp:
            # Add edge between v and neighbor to internal edges
            I_tmp.add(frozenset([v, neighbour]))

    # Remove edges no longer in the boundary
    for removed_node in removed_B_nodes:
        for removed_node_neighbour in G[removed_node]:
            if removed_node_neighbour not in B_tmp:
                T_tmp.discard(frozenset([removed_node_neighbour, removed_node]))
                I_tmp.discard(frozenset([removed_node_neighbour, removed_node]))

    R_tmp = len(I_tmp) / len(T_tmp) if len(T_tmp) > 0 else 1
    return R_tmp, B_tmp, T_tmp, I_tmp
