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
    fraction of all-pairs shortest paths that pass through any node in $C$

    .. math::

       c_B(v) =\sum_{s,t \in V-C} \frac{\sigma(s, t|v)}{\sigma(s, t)}

    where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
    shortest $(s, t)$-paths, and $\sigma(s, t|C)$ is the number of
    those paths passing through some node in group $C$. Note that
    $(s, t)$ are not members of the group ($V-C$ is the set of nodes
    in $V$ that are not in $C$ -- see `endpoints` for other options).

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
       both counting endpoints of paths and allowing node-pairs in C.

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

                for y in group:
                    # ensure y is in Dx, otherwise none of 3 Orders occur so skip
                    if y not in Dx:
                        continue
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
            GBC_group /= Nscale * (Nscale - 1) if Nscale > 1 else 1
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
    PB = dict.fromkeys(set_v)
    for x in set_v:
        PB[x] = dict.fromkeys(set_v, 0.0)
    for s in G:
        Ds = D[s]
        delta_s = delta[s]
        sig_s = sigma[s]
        s_descendants = set_v & Ds.keys()
        for x in s_descendants:
            Dx = D[x]
            Dsx = Ds[x]
            sig_x = sigma[x]
            sig_sx = sig_s[x]
            for y in s_descendants & Dx.keys():
                if Ds[y] == Dsx + Dx[y]:
                    PB[x][y] += delta_s[y] * sig_sx * sig_x[y] / sig_s[y]
    return PB, sigma, D


@nx._dispatchable(edge_attrs="weight")
def prominent_group(
    G, k, weight=None, C=None, endpoints=False, normalized=True, greedy=False
):
    r"""Find the prominent group (and its centrality) of size $k$ in graph $G$.

    The prominent group of nodes has the highest group betweenness centrality.
    Group betweenness centrality of a group of nodes $C$ is the sum of the
    fraction of all-pairs shortest paths that pass through any node in $C$

    .. math::

       c_B(v) =\sum_{s,t \in V-C} \frac{\sigma(s, t|v)}{\sigma(s, t)}

    where $V$ is the set of nodes, $\sigma(s, t)$ is the number of
    shortest $(s, t)$-paths, and $\sigma(s, t|C)$ is the number of
    those paths passing through some node in group $C$. Note that
    $(s, t)$ are not members of the group ($V-C$ is the set of nodes
    in $V$ that are not in $C$ -- see `endpoints` for other options).

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
       By default, only node-pairs that are both not in the group are counted for
       group betweenness centrality. The count is how many non-`C` node-pairs have
       nodes from the group "between" them on a shortest path.

       When ``endpoints=True``, we also count node-pairs with one or both nodes
       in the group while considering endpoint nodes as being between the node-pairs.
       So we count paths that start in the group whether or not they pass through
       any other nodes in the group. This adds centrality to large groups without any
       reference to the connectivity of the group. The minimum normalized score
       is $N_{in}(N_{in}-1)/(N(N-1))$ instead of 0. For that reason, this feature
       is rarely used.

       We don't currently support considering node-pairs with nodes in the group without
       also counting their endpoints. Nor do we support counting endpoints while only
       considering node-pairs that are both not in the group. This keyword indicates
       both counting endpoints of paths and allowing node-pairs in the group.

    C : list or set, optional (default=None)
       list of nodes which won't be candidates of the prominent group.

    greedy : bool, optional (default=False)
       Using a naive greedy algorithm in order to find non-optimal prominent
       group. For scale free networks the results are negligibly below the optimal
       results.

    Returns
    -------
    max_GBC, max_group : 2-tuple of (float, list or nodes)
       A 2-tuple of the group betweenness centrality of the prominent group,
       and a list of nodes in the prominent group.

    Raises
    ------
    NodeNotFound
       If any node(s) in C are not present in G.

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
    if C is not None:
        C = set(C)
        if C - G.nodes:  # element(s) of C not in G
            raise nx.NodeNotFound(f"The node(s) {C - G.nodes} are in C but not in G.")
        nodes = list(G.nodes - C)
    else:
        nodes = list(G.nodes)

    # pre-process connectedness for no endpoints treatment
    is_directed = G.is_directed()
    connected = nx.is_strongly_connected(G) if is_directed else nx.is_connected(G)

    PB, sigma, D = _group_preprocessing(G, nodes, weight)
    # top remaining nodes sorted by partial betweenness (PB)
    tops = sorted(nodes, key=lambda n: PB[n][n])
    heu = sum(PB[node][node] for node in tops[-k:])
    info = {"GBC": 0, "Grp": [], "tops": tops, "PB": PB, "sigma": sigma, "heu": heu}

    # the algorithm
    max_GBC, max_group = _prominent(k, info, D, nodes, greedy)

    # endpoints
    N = len(G)
    if endpoints:
        Nscale = N
    else:
        N_in = k
        N_out = Nscale = N - N_in
        # if the graph is connected then subtract the endpoints from
        # the count for all the nodes in the graph. else count how many
        # nodes are connected to the group's nodes and subtract that.
        if connected:
            extra = N_in * (N - 1 + N_out)
        elif is_directed:
            # count paths for group to or from anything
            reachables = ((u, v) for u in G for v in D[u] if v != u)
            extra = sum(1 for u, v in reachables if (u in max_group or v in max_group))
        else:
            # count paths for group to anything
            # (use 2 if v not in group to shorten reachables)
            reachables = ((u, v) for u in max_group for v in D[u] if v != u)
            extra = sum((1 if v in max_group else 2) for u, v in reachables)
        max_GBC -= extra

    # normalize
    if normalized:
        max_GBC /= Nscale * (Nscale - 1) if Nscale > 1 else 1
    # If undirected then count only the undirected edges
    elif not is_directed:
        max_GBC /= 2
    return max_GBC, max_group


def _prominent(k, info, D, nodes, greedy):
    """Return the GBC and the group of k nodes with the biggest GBC value"""
    max_GBC = 0
    max_group = []
    queue = [info]
    its = 0

    while queue:
        info = queue.pop()
        # info:
        #   "sigma": dod[s][t], count of s-t paths thru group nodes
        #   "PB": path btwn, dod[s][v], fraction of paths from s through v
        Grp = info["Grp"]  # list : group being considered
        GBC = info["GBC"]  # number : group betweenness centrality of the group
        tops = info["tops"]  # list : candidate nodes for Grp sorted by heuristic
        heu = info["heu"]  # dict : {node: max GBC change when adding node}
        # We use heuristic h4 from article: max sum_v PB[v][v] for best nodes
        # Names: the article uses names replaced here as:
        # GM<->Grp, CL<->tops, g<->GBC, h<->heu

        # Stopping conditions: go to next item on queue
        if GBC > max_GBC and len(Grp) == k:  # new max with group of size k found
            max_GBC = GBC
            max_group = Grp
            continue
        if len(Grp) == k or len(tops) <= k - len(Grp) or GBC + heu <= max_GBC:
            continue

        # add to the queue
        new_info = deepcopy(info)

        sigma = new_info["sigma"]
        PB = new_info["PB"]
        tops = new_info["tops"]
        v = tops.pop()
        new_info["Grp"].append(v)
        # Key step in updating GBC
        new_info["GBC"] += PB[v][v]

        # loop over all pairs of nodes (x, y); update PB and sigma
        Dv = D[v]
        PB_v = PB[v]
        sig_v = sigma[v]

        for x in nodes:
            # store lookups and set
            Dx = D[x]
            PB_x = PB[x]
            sig_x = sigma[x]
            sig_xv = sig_x[v]
            sig_vx = sig_v[x]
            x_in_Dv = x in Dv
            v_in_Dx = v in Dx

            # ensure y is in Dx otherwise none of the 3 Orders occur, so skip
            for y in (n for n in nodes if n in Dx):
                # store lookups
                Dy = D[y]
                sig_xy = sig_x[y]
                sig_vy = sig_v[y]
                v_in_Dy = v in Dy
                y_in_Dv = y in Dv

                # Order x-y-v  If v_in_Dy then v_in_Dx for sure.
                if v_in_Dy and Dx[v] == Dx[y] + Dy[v] and sig_xv:
                    if y != v:
                        PB_x[y] -= PB_x[v] * sig_xy * sigma[y][v] / sig_xv
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

        # update tops and heu
        new_info["tops"] = tops = sorted(tops, key=lambda n: PB[n][n])
        top_few = k - len(new_info["Grp"])
        new_info["heu"] = sum(PB[n][n] for n in tops[-top_few:]) if top_few else 0

        if greedy:
            queue.append(new_info)
            continue

        # not greedy: add the "minus" version and the new_info (plus version)
        m_info = deepcopy(info)
        top_few = k - len(m_info["Grp"])
        m_tops = m_info["tops"]
        m_tops.pop()
        PB = m_info["PB"]
        m_info["heu"] = sum(PB[n][n] for n in m_tops[-top_few:]) if top_few else 0

        if new_info["GBC"] + new_info["heu"] > m_info["GBC"] + m_info["heu"]:
            queue.append(m_info)
            queue.append(new_info)
        else:
            queue.append(new_info)
            queue.append(m_info)
    return max_GBC, max_group


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
