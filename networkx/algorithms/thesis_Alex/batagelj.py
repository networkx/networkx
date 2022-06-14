__all__ = [
    "batagelj_distances_shortest_paths",
    "batagelj_calculate_betweenness",
    "batagelj_betweenness_centrality",
    "batagelj_calculate_group_betweenness",
    "batagelj_group_betweenness_centrality",
]


def batagelj_distances_shortest_paths(G, weight="weight"):
    """Calculate distance, and number of shortest paths for all nodes in a graph.

    Parameters
    ----------
    G : NetworkX graph

    terminate_early : terminate early

    weight: string, optional (default= 'weight')
       Edge data key corresponding to the edge weight.

    Returns
    -------
    BC values : dictionary
       Dictionary keyed by node ids

    """
    from collections import defaultdict

    # dictionary-of-dictionaries representation for relationship matrix rel
    # use some defaultdict magic here
    # for rel the default is tuple (inf, 0)
    d_mtrx = defaultdict(lambda: defaultdict(lambda: float("inf")))

    sp_mtrx = defaultdict(lambda: defaultdict(lambda: 0))

    # set the distance to self to 0 (zero diagonal)
    for v in G:
        d_mtrx[v][v] = 0

    undirected = not G.is_directed()

    # traverses all edges
    for u, v, d in G.edges(data=True):
        e_weight = d.get(weight, 1.0)
        d_mtrx[u][v], sp_mtrx[u][v] = min(e_weight, d_mtrx[u][v]), 1
        if undirected:
            d_mtrx[v][u], sp_mtrx[v][u] = min(e_weight, d_mtrx[v][u]), 1

    for v in G:
        d_mtrx_v = d_mtrx[v]  # save recomputation
        for s in G:
            d_mtrx_s = d_mtrx[s]  # save recomputation
            for t in G:
                dist = min(float("inf"), d_mtrx_s[v] + d_mtrx_v[t])
                if d_mtrx_s[t] >= dist:
                    sps = sp_mtrx[s][v] * sp_mtrx[v][t]
                    if d_mtrx_s[t] == dist:
                        sp_mtrx[s][t] += sps
                    else:
                        d_mtrx_s[t], sp_mtrx[s][t] = dist, sps

    return d_mtrx, sp_mtrx


def batagelj_calculate_betweenness(G, dist_mtrx, sp_mtrx):

    BC_G = dict.fromkeys(G.nodes(), 0)

    for v in G:
        d_mtrx_v, sp_mtrx_v = dist_mtrx[v], sp_mtrx[v]  # save recomputation
        for s in G:
            d_mtrx_s, sp_mtrx_s = dist_mtrx[s], sp_mtrx[s]  # save recomputation
            for t in G:
                if s != v != t and d_mtrx_s[v] + d_mtrx_v[t] == d_mtrx_s[t]:
                    if sp_mtrx_s[t] > 0:
                        BC_G[v] += (sp_mtrx_s[v] * sp_mtrx_v[t]) / sp_mtrx_s[t]
        BC_G[v] = BC_G[v] / 2

    return BC_G


def batagelj_calculate_group_betweenness(G, C, dist_mtrx, sp_mtrx):

    GBC = 0
    for s in G:
        d_mtrx_s, sp_mtrx_s = dist_mtrx[s], sp_mtrx[s]  # save recomputation
        for t in G:
            if s not in C and t not in C:
                GBC_max_C = 0
                for v in C:
                    if s != v != t and d_mtrx_s[v] + dist_mtrx[v][t] == d_mtrx_s[t]:
                        if sp_mtrx_s[t] > 0:
                            BC_v = (sp_mtrx_s[v] * sp_mtrx[v][t]) / sp_mtrx_s[t]
                            GBC_max_C = max(GBC_max_C, BC_v)
                GBC += GBC_max_C
    return GBC / 2


def batagelj_betweenness_centrality(G, weight="weight"):

    dist_mtrx, sp_mtrx = batagelj_distances_shortest_paths(G, weight)
    BC_G = batagelj_calculate_betweenness(G, dist_mtrx, sp_mtrx)

    return BC_G


def batagelj_group_betweenness_centrality(G, C, weight="weight"):
    dist_mtrx, sp_mtrx = batagelj_distances_shortest_paths(G, weight)
    GBC = batagelj_calculate_group_betweenness(G, C, dist_mtrx, sp_mtrx)

    return GBC
