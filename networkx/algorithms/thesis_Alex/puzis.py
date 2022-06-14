from copy import deepcopy

import networkx as nx


def group_betweenness_centrality(G, C, normalized=True, weight=None, endpoints=False):
    r"""Compute the group betweenness centrality for a group of nodes.

    Group betweenness centrality of a group of nodes $C$ is the sum of the
    fraction of all-pairs shortest paths that pass through any vertex in $C$

    .. math::

       c_B(v) =\sum_{s,t \in V} \frac{\sigma(s, t|v)}{\sigma(s, t)}

    where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
    shortest $(s, t)$-paths, and $\sigma(s, t|C)$ is the number of
    those paths passing through some node in group $C$. Note that
    $(s, t)$ are not members of the group ($V-C$ is the set of nodes
    in $V$ that are not in $C$).

    Parameters
    ----------
    G : graph
      A NetworkX graph.

    C : list or set or list of lists or list of sets
      A group or a list of groups containing nodes which belong to G, for which group betweenness
      centrality is to be calculated.

    normalized : bool, optional (default=True)
      If True, group betweenness is normalized by `1/((|V|-|C|)(|V|-|C|-1))`
      where `|V|` is the number of nodes in G and `|C|` is the number of nodes in C.

    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.
      The weight of an edge is treated as the length or distance between the two sides.

    endpoints : bool, optional (default=False)
      If True include the endpoints in the shortest path counts.

    Raises
    ------
    NodeNotFound
       If node(s) in C are not present in G.

    Returns
    -------
    betweenness : list of floats or float
       If C is a single group then return a float. If C is a list with
       several groups then return a list of group betweenness centralities.

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    Group betweenness centrality is described in [1]_ and its importance discussed in [3]_.
    The initial implementation of the algorithm is mentioned in [2]_. This function uses
    an improved algorithm presented in [4]_.

    The number of nodes in the group must be a maximum of n - 2 where `n`
    is the total number of nodes in the graph.

    For weighted graphs the edge weights must be greater than zero.
    Zero edge weights can produce an infinite number of equal length
    paths between pairs of nodes.

    The total number of paths between source and target is counted
    differently for directed and undirected graphs. Directed paths
    between "u" and "v" are counted as two possible paths (one each
    direction) while undirected paths between "u" and "v" are counted
    as one path. Said another way, the sum in the expression above is
    over all ``s != t`` for directed graphs and for ``s < t`` for undirected graphs.


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
    .. [4] Rami Puzis, Yuval Elovici, and Shlomi Dolev.
       "Fast algorithm for successive computation of group betweenness centrality."
       https://journals.aps.org/pre/pdf/10.1103/PhysRevE.76.056709

    """
    GBC = []  # initialize betweenness
    list_of_groups = True
    #  check weather C contains one or many groups
    if any(el in G for el in C):
        C = [C]
        list_of_groups = False
    set_v = {node for group in C for node in group}
    if set_v - G.nodes:  # element(s) of C not in G
        raise nx.NodeNotFound(f"The node(s) {set_v - G.nodes} are in C but not in G.")

    # pre-processing
    PB, sigma, D = _group_preprocessing(G, set_v, weight)

    # the algorithm for each group
    for group in C:
        group = set(group)  # set of nodes in group
        # initialize the matrices of the sigma and the PB
        GBC_group = 0
        sigma_m = deepcopy(sigma)
        PB_m = deepcopy(PB)
        sigma_m_v = deepcopy(sigma_m)
        PB_m_v = deepcopy(PB_m)
        for v in group:
            GBC_group += PB_m[v][v]
            for x in group:
                for y in group:
                    dxvy = 0
                    dxyv = 0
                    dvxy = 0
                    if not (
                        sigma_m[x][y] == 0 or sigma_m[x][v] == 0 or sigma_m[v][y] == 0
                    ):
                        if D[x][v] == D[x][y] + D[y][v]:
                            dxyv = sigma_m[x][y] * sigma_m[y][v] / sigma_m[x][v]
                        if D[x][y] == D[x][v] + D[v][y]:
                            dxvy = sigma_m[x][v] * sigma_m[v][y] / sigma_m[x][y]
                        if D[v][y] == D[v][x] + D[x][y]:
                            dvxy = sigma_m[v][x] * sigma[x][y] / sigma[v][y]
                    sigma_m_v[x][y] = sigma_m[x][y] * (1 - dxvy)
                    PB_m_v[x][y] = PB_m[x][y] - PB_m[x][y] * dxvy
                    if y != v:
                        PB_m_v[x][y] -= PB_m[x][v] * dxyv
                    if x != v:
                        PB_m_v[x][y] -= PB_m[v][y] * dvxy
            sigma_m, sigma_m_v = sigma_m_v, sigma_m
            PB_m, PB_m_v = PB_m_v, PB_m

        # endpoints
        v, c = len(G), len(group)
        if not endpoints:
            scale = 0
            # if the graph is connected then subtract the endpoints from
            # the count for all the nodes in the graph. else count how many
            # nodes are connected to the group's nodes and subtract that.
            if nx.is_directed(G):
                if nx.is_strongly_connected(G):
                    scale = c * (2 * v - c - 1)
            elif nx.is_connected(G):
                scale = c * (2 * v - c - 1)
            if scale == 0:
                for group_node1 in group:
                    for node in D[group_node1]:
                        if node != group_node1:
                            if node in group:
                                scale += 1
                            else:
                                scale += 2
            GBC_group -= scale

        # normalized
        if normalized:
            scale = 1 / ((v - c) * (v - c - 1))
            GBC_group *= scale

        # If undirected than count only the undirected edges
        elif not G.is_directed():
            GBC_group /= 2

        GBC.append(GBC_group)
    if list_of_groups:
        return GBC
    else:
        return GBC[0]


def _group_preprocessing(G, set_v, weight):
    sigma = {}
    delta = {}
    D = {}
    betweenness = dict.fromkeys(G, 0)
    for s in G:
        if weight is None:  # use BFS
            S, P, sigma[s], D[s] = _single_source_shortest_path_basic(G, s)
        else:  # use Dijkstra's algorithm
            S, P, sigma[s], D[s] = _single_source_dijkstra_path_basic(G, s, weight)
        betweenness, delta[s] = _accumulate_endpoints(betweenness, S, P, sigma[s], s)
        for i in delta[s].keys():  # add the paths from s to i and rescale sigma
            if s != i:
                delta[s][i] += 1
            if weight is not None:
                sigma[s][i] = sigma[s][i] / 2
    # building the path betweenness matrix only for nodes that appear in the group
    PB = dict.fromkeys(G)
    for group_node1 in set_v:
        PB[group_node1] = dict.fromkeys(G, 0.0)
        for group_node2 in set_v:
            if group_node2 not in D[group_node1]:
                continue
            for node in G:
                # if node is connected to the two group nodes than continue
                if group_node2 in D[node] and group_node1 in D[node]:
                    if (
                        D[node][group_node2]
                        == D[node][group_node1] + D[group_node1][group_node2]
                    ):
                        PB[group_node1][group_node2] += (
                            delta[node][group_node2]
                            * sigma[node][group_node1]
                            * sigma[group_node1][group_node2]
                            / sigma[node][group_node2]
                        )
    return PB, sigma, D
