"""Group centrality measures."""

from copy import deepcopy

import networkx as nx
from networkx.algorithms.centrality.betweenness import (
    _accumulate_endpoints,
    _single_source_dijkstra_path_basic,
    _single_source_shortest_path_basic,
)
from networkx.utils.decorators import not_implemented_for

__all__ = [
    "group_betweenness_centrality",
    "group_closeness_centrality",
    "group_degree_centrality",
    "group_in_degree_centrality",
    "group_out_degree_centrality",
    "prominent_group",
]


@nx._dispatchable(edge_attrs="weight")
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
      A group or a list of groups containing nodes which belong to G,
      for which group betweenness centrality is to be calculated.

    normalized : bool, optional (default=True)
      If True, group betweenness is normalized by $1/(N_{out}(N_{out}-1))$
      where $N_{out}$ is the number of nodes in `G` that are not in `C`.
      This ensures the reported value is between 0 and 1.
      If `endpoints` is True, the normalization uses all nodes in `G`.
      The reported value is then between $2N_{in}/(N-1)$ and 1 where $N_{in}$
      is the number of nodes in `C` and $N$ the number of nodes in `G`.

    weight : None or string, optional (default=None)
      If None, all edge weights are considered equal.
      Otherwise holds the name of the edge attribute used as weight.
      The weight of an edge is treated as the length or distance between the two sides.

    endpoints : bool, optional (default=False)
      By default, only node-pairs that are both not in `C` are counted for
      group betweenness centrality. The count is how many non-`C` node-pairs have
      nodes from `C` "between" them on a shortest path.

      When ``endpoints=True``, we also count node-pairs with one or both nodes
      in `C` while considering endpoint nodes as being between the node-pairs.
      So we count paths that start in `C` whether or not they pass through
      any other nodes in `C`. This adds centrality to large groups without any
      reference to the connectivity of the group. The minimum normalized score
      is $N_{in}(N_{in}-1)/(N(N-1))$ instead of 0. For that reason, this feature
      is rarely used.

      We don't currently support considering node-pairs with nodes in `C` without
      also counting their endpoints. Nor do we support counting endpoints while
      only considering node-pairs that are both not in `C`. This keyword indicates
      both coutning endpoints of paths and allowing node-pairs in C.

    Raises
    ------
    NodeNotFound
       If node(s) in `C` are not present in `G`.

    Returns
    -------
    betweenness : list of floats or float
       If `C` is a single group then return a float. If `C` is a list with
       several groups then return a list of group betweenness centralities.

    See Also
    --------
    betweenness_centrality

    Notes
    -----
    Group betweenness centrality is defined in [1]_ and discussed in [3]_.
    The algorithm is described in [2]_ and is based on techniques mentioned in [4]_.

    The number of nodes in the group must be a maximum of ``N - 2`` where ``N``
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
    # check whether C contains one or many groups
    if any(el in G for el in C):
        C = [C]
        list_of_groups = False
    set_v = {node for group in C for node in group}
    if set_v - G.nodes:  # element(s) of C not in G
        raise nx.NodeNotFound(f"The node(s) {set_v - G.nodes} are in C but not in G.")

    # pre-process connectedness for no endpoints treatment
    is_directed = G.is_directed()
    connected = nx.is_strongly_connected(G) if is_directed else nx.is_connected(G)

    # pre-process dict-of-dicts: path btwn(PB), short path counts(sigma), distances(D)
    PB, sigma, D = _group_preprocessing(G, set_v, weight)

    # Run the algorithm for each group
    for group in C:
        group = set(group)  # set of nodes in group
        # initialize the matrices sigma_m and PB_m (path betweenness)
        GBC_group = 0
        sigma_m = deepcopy(sigma)
        PB_m = deepcopy(PB)
        for v in group:
            # main point of this whole loop!
            GBC_group += PB_m[v][v]

            # store lookups
            Dv = D[v]
            PB_v = PB_m[v]
            sig_v = sigma_m[v]

            for x in group:
                # store lookups and set
                Dx = D[x]
                PB_x = PB_m[x]
                sig_x = sigma_m[x]
                sig_xv = sig_x[v]
                sig_vx = sig_v[x]
                x_in_Dv = x in Dv
                v_in_Dx = v in Dx

                # ensure y is in Dx otherwise all 3 Orders will not occur
                for y in group & Dx.keys():
                    # store lookups
                    Dy = D[y]
                    sig_xy = sig_x[y]
                    sig_vy = sig_v[y]
                    v_in_Dy = v in Dy
                    y_in_Dv = y in Dv

                    # Order x-y-v  If v_in_Dy then v_in_Dx for sure.
                    if v_in_Dy and Dx[v] == Dx[y] + Dy[v] and sig_xv:
                        if y != v:
                            PB_x[y] -= PB_x[v] * sig_xy * sigma_m[y][v] / sig_xv
                    # Order v-x-y  If x_in_Dv then y_in_Dv for sure.
                    if x_in_Dv and Dv[y] == Dv[x] + Dx[y] and sig_vy:
                        if x != v:
                            # fraction of v->y paths that pass through x
                            PB_x[y] -= PB_v[y] * sig_vx * sig_xy / sig_vy
                    # order x-v-y
                    if v_in_Dx and y_in_Dv and Dx[y] == Dx[v] + Dv[y] and sig_xy:
                        sig_xvy = sig_xv * sig_vy
                        PB_x[y] *= 1 - sig_xvy / sig_xy
                        sig_x[y] -= sig_xvy
                        if y == v:
                            # update sig_xv for future y-values
                            sig_xv -= sig_xvy
        # endpoints
        N = len(G)
        if endpoints:
            Nscale = N
        else:  # No endpoints -- usual case
            N_in = len(group)
            N_out = Nscale = N - N_in
            # if the graph is connected then subtract the endpoints from
            # the count for all the nodes in the graph. else count how many
            # nodes are connected to the group's nodes and subtract that.
            if connected:
                # N_in * (N_out + N_in-1 + N_out) : in*out + in*(in-1) + out*in
                # same as N_in * (N-1 + N_out) : in*(all-1) + out*in
                # paper uses equiv: N_in * (2 * N - N_in - 1)
                extra = N_in * (N - 1 + N_out)
            elif is_directed:
                # count paths for group to or from anything
                reachables = ((u, v) for u in G for v in D[u] if v != u)
                extra = sum(1 for u, v in reachables if (u in group or v in group))
            else:
                # count paths for group to anything
                # (use 2 if v not in group to shorten reachables)
                reachables = ((u, v) for u in group for v in D[u] if v != u)
                extra = sum((1 if v in group else 2) for u, v in reachables)

            GBC_group -= extra

        # scale down for normalized or by 2 for undirected
        if normalized:
            GBC_group /= Nscale * (Nscale - 1)
        elif not is_directed:
            GBC_group /= 2

        GBC.append(GBC_group)
    if list_of_groups:
        return GBC
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
        for i in delta[s]:  # add the paths from s to i and rescale sigma
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


@nx._dispatchable(edge_attrs="weight")
def prominent_group(
    G, k, weight=None, C=None, endpoints=False, normalized=True, greedy=False
):
    r"""Find the prominent group of size $k$ in graph $G$. The prominence of the
    group is evaluated by the group betweenness centrality.

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

    k : int
       The number of nodes in the group.

    normalized : bool, optional (default=True)
       If True, group betweenness is normalized by ``1/((|V|-|C|)(|V|-|C|-1))``
       where ``|V|`` is the number of nodes in G and ``|C|`` is the number of
       nodes in C.

    weight : None or string, optional (default=None)
       If None, all edge weights are considered equal.
       Otherwise holds the name of the edge attribute used as weight.
       The weight of an edge is treated as the length or distance between the two sides.

    endpoints : bool, optional (default=False)
       If True include the endpoints in the shortest path counts.

    C : list or set, optional (default=None)
       list of nodes which won't be candidates of the prominent group.

    greedy : bool, optional (default=False)
       Using a naive greedy algorithm in order to find non-optimal prominent
       group. For scale free networks the results are negligibly below the optimal
       results.

    Raises
    ------
    NodeNotFound
       If node(s) in C are not present in G.

    Returns
    -------
    max_GBC : float
       The group betweenness centrality of the prominent group.

    max_group : list
        The list of nodes in the prominent group.

    See Also
    --------
    betweenness_centrality, group_betweenness_centrality

    Notes
    -----
    Group betweenness centrality is defined in [1]_ and discussed in [3]_.
    The algorithm is described in [2]_ and is based on techniques mentioned in [4]_.

    The number of nodes in the group must be a maximum of ``N - 2`` where ``N``
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
    .. [2] Rami Puzis, Yuval Elovici, and Shlomi Dolev:
       "Finding the Most Prominent Group in Complex Networks"
       AI communications 20(4): 287-296, 2007.
       https://www.researchgate.net/profile/Rami_Puzis2/publication/220308855
    .. [3] Sourav Medya et. al.:
       Group Centrality Maximization via Network Design.
       SIAM International Conference on Data Mining, SDM 2018, 126–134.
       https://sites.cs.ucsb.edu/~arlei/pubs/sdm18.pdf
    .. [4] Rami Puzis, Yuval Elovici, and Shlomi Dolev.
       "Fast algorithm for successive computation of group betweenness centrality."
       https://journals.aps.org/pre/pdf/10.1103/PhysRevE.76.056709
    """
    import numpy as np
    import pandas as pd

    if C is not None:
        C = set(C)
        if C - G.nodes:  # element(s) of C not in G
            raise nx.NodeNotFound(f"The node(s) {C - G.nodes} are in C but not in G.")
        nodes = list(G.nodes - C)
    else:
        nodes = list(G.nodes)
    DF_tree = nx.Graph()
    DF_tree.__networkx_cache__ = None  # Disable caching
    PB, sigma, D = _group_preprocessing(G, nodes, weight)
    betweenness = pd.DataFrame.from_dict(PB)
    if C is not None:
        for node in C:
            # remove from the betweenness all the nodes not part of the group
            betweenness = betweenness.drop(index=node)
            betweenness = betweenness.drop(columns=node)
    CL = [node for _, node in sorted(zip(np.diag(betweenness), nodes), reverse=True)]
    max_GBC = 0
    max_group = []
    DF_tree.add_node(
        1,
        CL=CL,
        betweenness=betweenness,
        GBC=0,
        GM=[],
        sigma=sigma,
        cont=dict(zip(nodes, np.diag(betweenness))),
    )

    # the algorithm
    DF_tree.nodes[1]["heu"] = 0
    for i in range(k):
        DF_tree.nodes[1]["heu"] += DF_tree.nodes[1]["cont"][DF_tree.nodes[1]["CL"][i]]
    max_GBC, DF_tree, max_group = _dfbnb(
        G, k, DF_tree, max_GBC, 1, D, max_group, nodes, greedy
    )

    v = len(G)
    if not endpoints:
        scale = 0
        # if the graph is connected then subtract the endpoints from
        # the count for all the nodes in the graph. else count how many
        # nodes are connected to the group's nodes and subtract that.
        if nx.is_directed(G):
            if nx.is_strongly_connected(G):
                scale = k * (2 * v - k - 1)
        elif nx.is_connected(G):
            scale = k * (2 * v - k - 1)
        if scale == 0:
            for group_node1 in max_group:
                for node in D[group_node1]:
                    if node != group_node1:
                        if node in max_group:
                            scale += 1
                        else:
                            scale += 2
        max_GBC -= scale

    # normalized
    if normalized:
        scale = 1 / ((v - k) * (v - k - 1))
        max_GBC *= scale

    # If undirected then count only the undirected edges
    elif not G.is_directed():
        max_GBC /= 2
    max_GBC = float(f"{max_GBC:.2f}")
    return max_GBC, max_group


def _dfbnb(G, k, DF_tree, max_GBC, root, D, max_group, nodes, greedy):
    # stopping condition - if we found a group of size k and with higher GBC then prune
    if len(DF_tree.nodes[root]["GM"]) == k and DF_tree.nodes[root]["GBC"] > max_GBC:
        return DF_tree.nodes[root]["GBC"], DF_tree, DF_tree.nodes[root]["GM"]
    # stopping condition - if the size of group members equal to k or there are less than
    # k - |GM| in the candidate list or the heuristic function plus the GBC is below the
    # maximal GBC found then prune
    if (
        len(DF_tree.nodes[root]["GM"]) == k
        or len(DF_tree.nodes[root]["CL"]) <= k - len(DF_tree.nodes[root]["GM"])
        or DF_tree.nodes[root]["GBC"] + DF_tree.nodes[root]["heu"] <= max_GBC
    ):
        return max_GBC, DF_tree, max_group

    # finding the heuristic of both children
    node_p, node_m, DF_tree = _heuristic(k, root, DF_tree, D, nodes, greedy)

    # finding the child with the bigger heuristic + GBC and expand
    # that node first if greedy then only expand the plus node
    if greedy:
        max_GBC, DF_tree, max_group = _dfbnb(
            G, k, DF_tree, max_GBC, node_p, D, max_group, nodes, greedy
        )

    elif (
        DF_tree.nodes[node_p]["GBC"] + DF_tree.nodes[node_p]["heu"]
        > DF_tree.nodes[node_m]["GBC"] + DF_tree.nodes[node_m]["heu"]
    ):
        max_GBC, DF_tree, max_group = _dfbnb(
            G, k, DF_tree, max_GBC, node_p, D, max_group, nodes, greedy
        )
        max_GBC, DF_tree, max_group = _dfbnb(
            G, k, DF_tree, max_GBC, node_m, D, max_group, nodes, greedy
        )
    else:
        max_GBC, DF_tree, max_group = _dfbnb(
            G, k, DF_tree, max_GBC, node_m, D, max_group, nodes, greedy
        )
        max_GBC, DF_tree, max_group = _dfbnb(
            G, k, DF_tree, max_GBC, node_p, D, max_group, nodes, greedy
        )
    return max_GBC, DF_tree, max_group


def _heuristic(k, root, DF_tree, D, nodes, greedy):
    import numpy as np

    # This helper function add two nodes to DF_tree - one left son and the
    # other right son, finds their heuristic, CL, GBC, and GM
    node_p = DF_tree.number_of_nodes() + 1
    node_m = DF_tree.number_of_nodes() + 2
    added_node = DF_tree.nodes[root]["CL"][0]

    # adding the plus node
    DF_tree.add_nodes_from([(node_p, deepcopy(DF_tree.nodes[root]))])
    DF_tree.nodes[node_p]["GM"].append(added_node)
    DF_tree.nodes[node_p]["GBC"] += DF_tree.nodes[node_p]["cont"][added_node]
    root_node = DF_tree.nodes[root]
    for x in nodes:
        for y in nodes:
            dxvy = 0
            dxyv = 0
            dvxy = 0
            if not (
                root_node["sigma"][x][y] == 0
                or root_node["sigma"][x][added_node] == 0
                or root_node["sigma"][added_node][y] == 0
            ):
                if D[x][added_node] == D[x][y] + D[y][added_node]:
                    dxyv = (
                        root_node["sigma"][x][y]
                        * root_node["sigma"][y][added_node]
                        / root_node["sigma"][x][added_node]
                    )
                if D[x][y] == D[x][added_node] + D[added_node][y]:
                    dxvy = (
                        root_node["sigma"][x][added_node]
                        * root_node["sigma"][added_node][y]
                        / root_node["sigma"][x][y]
                    )
                if D[added_node][y] == D[added_node][x] + D[x][y]:
                    dvxy = (
                        root_node["sigma"][added_node][x]
                        * root_node["sigma"][x][y]
                        / root_node["sigma"][added_node][y]
                    )
            DF_tree.nodes[node_p]["sigma"][x][y] = root_node["sigma"][x][y] * (1 - dxvy)
            DF_tree.nodes[node_p]["betweenness"].loc[y, x] = (
                root_node["betweenness"][x][y] - root_node["betweenness"][x][y] * dxvy
            )
            if y != added_node:
                DF_tree.nodes[node_p]["betweenness"].loc[y, x] -= (
                    root_node["betweenness"][x][added_node] * dxyv
                )
            if x != added_node:
                DF_tree.nodes[node_p]["betweenness"].loc[y, x] -= (
                    root_node["betweenness"][added_node][y] * dvxy
                )

    DF_tree.nodes[node_p]["CL"] = [
        node
        for _, node in sorted(
            zip(np.diag(DF_tree.nodes[node_p]["betweenness"]), nodes), reverse=True
        )
        if node not in DF_tree.nodes[node_p]["GM"]
    ]
    DF_tree.nodes[node_p]["cont"] = dict(
        zip(nodes, np.diag(DF_tree.nodes[node_p]["betweenness"]))
    )
    DF_tree.nodes[node_p]["heu"] = 0
    for i in range(k - len(DF_tree.nodes[node_p]["GM"])):
        DF_tree.nodes[node_p]["heu"] += DF_tree.nodes[node_p]["cont"][
            DF_tree.nodes[node_p]["CL"][i]
        ]

    # adding the minus node - don't insert the first node in the CL to GM
    # Insert minus node only if isn't greedy type algorithm
    if not greedy:
        DF_tree.add_nodes_from([(node_m, deepcopy(DF_tree.nodes[root]))])
        DF_tree.nodes[node_m]["CL"].pop(0)
        DF_tree.nodes[node_m]["cont"].pop(added_node)
        DF_tree.nodes[node_m]["heu"] = 0
        for i in range(k - len(DF_tree.nodes[node_m]["GM"])):
            DF_tree.nodes[node_m]["heu"] += DF_tree.nodes[node_m]["cont"][
                DF_tree.nodes[node_m]["CL"][i]
            ]
    else:
        node_m = None

    return node_p, node_m, DF_tree


@nx._dispatchable(edge_attrs="weight")
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
       The weight of an edge is treated as the length or distance between the two sides.

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

    The number of nodes in the group must be a maximum of ``N - 1`` where ``N``
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
       https://doi.org/10.1145/2567948.2579356
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


@nx._dispatchable
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
    centrality = len(set().union(*[set(G.neighbors(i)) for i in S]) - set(S))
    centrality /= len(G.nodes()) - len(S)
    return centrality


@not_implemented_for("undirected")
@nx._dispatchable
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
@nx._dispatchable
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
