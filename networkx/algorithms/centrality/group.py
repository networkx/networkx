"""Group centrality measures."""
from itertools import combinations


import networkx as nx
from networkx.utils.decorators import not_implemented_for


__all__ = [
    "group_betweenness_centrality",
    "group_closeness_centrality",
    "group_degree_centrality",
    "group_in_degree_centrality",
    "group_out_degree_centrality",
]


def group_betweenness_centrality(G, C, normalized=True, weight=None):
    r"""Compute the group betweenness centrality for a group of nodes.

    Group betweenness centrality of a group of nodes $C$ is the sum of the
    fraction of all-pairs shortest paths that pass through any vertex in $C$

    .. math::

       c_B(C) =\sum_{s,t \in V-C; s<t} \frac{\sigma(s, t|C)}{\sigma(s, t)}

    where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
    shortest $(s, t)$-paths, and $\sigma(s, t|C)$ is the number of
    those paths passing through some node in group $C$. Note that
    $(s, t)$ are not members of the group ($V-C$ is the set of nodes
    in $V$ that are not in $C$).

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    C : list or set
      C is a group of nodes which belong to G, for which group betweenness
      centrality is to be calculated.

    normalized : bool, optional
      If True, group betweenness is normalized by `2/((|V|-|C|)(|V|-|C|-1))`
      for graphs and `1/((|V|-|C|)(|V|-|C|-1))` for directed graphs where `|V|`
      is the number of nodes in G and `|C|` is the number of nodes in C.

    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.

    Raises
    ------
    NodeNotFound
       If node(s) in C are not present in G.

    Returns
    -------
    betweenness : float
       Group betweenness centrality of the group C.

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    The measure is described in [1]_.
    The algorithm is an extension of the one proposed by Ulrik Brandes for
    betweenness centrality of nodes. Group betweenness is also mentioned in
    his paper [2]_ along with the algorithm. The importance of the measure is
    discussed in [3]_.

    The number of nodes in the group must be a maximum of n - 2 where `n`
    is the total number of nodes in the graph.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length
    paths between pairs of nodes.

    References
    ----------
    .. [1] M G Everett and S P Borgatti:
       The Centrality of Groups and Classes.
       Journal of Mathematical Sociology. 23(3): 181-201. 1999.
       http://www.analytictech.com/borgatti/group_centrality.htm
    .. [2] Ulrik Brandes:
       On Variants of Shortest-Path Betweenness
       Centrality and their Generic Computation.
       Social Networks 30(2):136-145, 2008.
       http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.72.9610&rep=rep1&type=pdf
    .. [3] Sourav Medya et. al.:
       Group Centrality Maximization via Network Design.
       SIAM International Conference on Data Mining, SDM 2018, 126–134.
       https://sites.cs.ucsb.edu/~arlei/pubs/sdm18.pdf
    """
    betweenness = 0  # initialize betweenness to 0
    V = set(G)  # set of nodes in G
    C = set(C)  # set of nodes in C (group)
    if len(C - V) != 0:  # element(s) of C not in V
        raise nx.NodeNotFound(
            "The node(s) " + str(list(C - V)) + " are not " "in the graph."
        )
    V_C = V - C  # set of nodes in V but not in C
    # accumulation
    for pair in combinations(V_C, 2):  # (s, t) pairs of V_C
        try:
            paths = 0
            paths_through_C = 0
            for path in nx.all_shortest_paths(
                G, source=pair[0], target=pair[1], weight=weight
            ):
                if set(path) & C:
                    paths_through_C += 1
                paths += 1
            betweenness += paths_through_C / paths
        except nx.exception.NetworkXNoPath:
            betweenness += 0
    # rescaling
    v, c = len(G), len(C)
    if normalized:
        scale = 1 / ((v - c) * (v - c - 1))
        if not G.is_directed():
            scale *= 2
    else:
        scale = None
    if scale is not None:
        betweenness *= scale
    return betweenness


def group_closeness_centrality(G, S, weight=None):
    r"""Compute the group closeness centrality for a group of nodes.

    Group closeness centrality of a group of nodes $S$ is a measure
    of how close the group is to the other nodes in the graph.

    .. math::

       c_{close}(S) = \frac{|V-S|}{\sum_{v \in V-S} d_{S, v}}

       d_{S, v} = min_{u \in S} (d_{u, v})

    where $V$ is the set of nodes, $d_{S, v}$ is the distance of
    the group $S$ from $v$ defined as above. ($V-S$ is the set of nodes
    in $V$ that are not in $S$).

    Parameters
    ----------
    G : graph
       A NetworkX graph.

    S : list or set
       S is a group of nodes which belong to G, for which group closeness
       centrality is to be calculated.

    weight : None or string, optional (default=None)
       If None, all edge weights are considered equal.
       Otherwise holds the name of the edge attribute used as weight.

    Raises
    ------
    NodeNotFound
       If node(s) in S are not present in G.

    Returns
    -------
    closeness : float
       Group closeness centrality of the group S.

    See Also
    --------
    closeness_centrality

    Notes
    -----
    The measure was introduced in [1]_.
    The formula implemented here is described in [2]_.

    Higher values of closeness indicate greater centrality.

    It is assumed that 1 / 0 is 0 (required in the case of directed graphs,
    or when a shortest path length is 0).

    The number of nodes in the group must be a maximum of n - 1 where `n`
    is the total number of nodes in the graph.

    For directed graphs, the incoming distance is utilized here. To use the
    outward distance, act on `G.reverse()`.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length
    paths between pairs of nodes.

    References
    ----------
    .. [1] M G Everett and S P Borgatti:
       The Centrality of Groups and Classes.
       Journal of Mathematical Sociology. 23(3): 181-201. 1999.
       http://www.analytictech.com/borgatti/group_centrality.htm
    .. [2] J. Zhao et. al.:
       Measuring and Maximizing Group Closeness Centrality over
       Disk Resident Graphs.
       WWWConference Proceedings, 2014. 689-694.
       http://wwwconference.org/proceedings/www2014/companion/p689.pdf
    """
    if G.is_directed():
        G = G.reverse()  # reverse view
    closeness = 0  # initialize to 0
    V = set(G)  # set of nodes in G
    S = set(S)  # set of nodes in group S
    V_S = V - S  # set of nodes in V but not S
    shortest_path_lengths = nx.multi_source_dijkstra_path_length(G, S, weight=weight)
    # accumulation
    for v in V_S:
        try:
            closeness += shortest_path_lengths[v]
        except KeyError:  # no path exists
            closeness += 0
    try:
        closeness = len(V_S) / closeness
    except ZeroDivisionError:  # 1 / 0 assumed as 0
        closeness = 0
    return closeness


def group_degree_centrality(G, S):
    """Compute the group degree centrality for a group of nodes.

    Group degree centrality of a group of nodes $S$ is the fraction
    of non-group members connected to group members.

    Parameters
    ----------
    G : graph
       A NetworkX graph.

    S : list or set
       S is a group of nodes which belong to G, for which group degree
       centrality is to be calculated.

    Raises
    ------
    NetworkXError
       If node(s) in S are not in G.

    Returns
    -------
    centrality : float
       Group degree centrality of the group S.

    See Also
    --------
    degree_centrality
    group_in_degree_centrality
    group_out_degree_centrality

    Notes
    -----
    The measure was introduced in [1]_.

    The number of nodes in the group must be a maximum of n - 1 where `n`
    is the total number of nodes in the graph.

    References
    ----------
    .. [1] M G Everett and S P Borgatti:
       The Centrality of Groups and Classes.
       Journal of Mathematical Sociology. 23(3): 181-201. 1999.
       http://www.analytictech.com/borgatti/group_centrality.htm
    """
    centrality = len(set().union(*list(set(G.neighbors(i)) for i in S)) - set(S))
    centrality /= len(G.nodes()) - len(S)
    return centrality


@not_implemented_for("undirected")
def group_in_degree_centrality(G, S):
    """Compute the group in-degree centrality for a group of nodes.

    Group in-degree centrality of a group of nodes $S$ is the fraction
    of non-group members connected to group members by incoming edges.

    Parameters
    ----------
    G : graph
       A NetworkX graph.

    S : list or set
       S is a group of nodes which belong to G, for which group in-degree
       centrality is to be calculated.

    Returns
    -------
    centrality : float
       Group in-degree centrality of the group S.

    Raises
    ------
    NetworkXNotImplemented
       If G is undirected.

    NodeNotFound
       If node(s) in S are not in G.

    See Also
    --------
    degree_centrality
    group_degree_centrality
    group_out_degree_centrality

    Notes
    -----
    The number of nodes in the group must be a maximum of n - 1 where `n`
    is the total number of nodes in the graph.

    `G.neighbors(i)` gives nodes with an outward edge from i, in a DiGraph,
    so for group in-degree centrality, the reverse graph is used.
    """
    return group_degree_centrality(G.reverse(), S)


@not_implemented_for("undirected")
def group_out_degree_centrality(G, S):
    """Compute the group out-degree centrality for a group of nodes.

    Group out-degree centrality of a group of nodes $S$ is the fraction
    of non-group members connected to group members by outgoing edges.

    Parameters
    ----------
    G : graph
       A NetworkX graph.

    S : list or set
       S is a group of nodes which belong to G, for which group in-degree
       centrality is to be calculated.

    Returns
    -------
    centrality : float
       Group out-degree centrality of the group S.

    Raises
    ------
    NetworkXNotImplemented
       If G is undirected.

    NodeNotFound
       If node(s) in S are not in G.

    See Also
    --------
    degree_centrality
    group_degree_centrality
    group_in_degree_centrality

    Notes
    -----
    The number of nodes in the group must be a maximum of n - 1 where `n`
    is the total number of nodes in the graph.

    `G.neighbors(i)` gives nodes with an outward edge from i, in a DiGraph,
    so for group out-degree centrality, the graph itself is used.
    """
    return group_degree_centrality(G, S)
