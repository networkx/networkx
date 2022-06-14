from collections import deque

__all__ = [
    "brandes_group_betweenness_centrality",
]


def brandes_group_betweenness_centrality(G, C):
    r"""Compute the shortest-path group betweenness centrality for the set C.

    Betweenness centrality of a set node $C$ is the sum of the
    fraction of all-pairs shortest paths that pass through 1 or more nodes in $C$

    Only implemented for undirected, unweighted graphs.

    G : graph
      A NetworkX graph.

    C : list or set or list of lists or list of sets
      A group or a list of groups containing nodes which belong to G, for which group betweenness
      centrality is to be calculated.
    """
    GBC = 0
    for s in G:
        if s not in C:
            S, P, sigma, _ = _single_source_shortest_path_basic(G, s)
            GBC += _accumulate_group(C, S, P, sigma, s)
    return GBC/2


def _single_source_shortest_path_basic(G, s):
    S = []
    P = {}
    for v in G:
        P[v] = []
    sigma = dict.fromkeys(G, 0.0)  # sigma[v]=0 for v in G
    D = {}
    sigma[s] = 1.0
    D[s] = 0
    Q = deque([s])
    while Q:  # use BFS to find shortest paths
        v = Q.popleft()
        S.append(v)
        Dv = D[v]
        sigmav = sigma[v]
        for w in G[v]:
            if w not in D:
                Q.append(w)
                D[w] = Dv + 1
            if D[w] == Dv + 1:  # this is a shortest path, count paths
                sigma[w] += sigmav
                P[w].append(v)  # predecessors
    return S, P, sigma, D


def _accumulate_group(C, S, P, sigma, s):
    delta = dict.fromkeys(S, 0)
    GBC = 0
    C_no_s = set(C) - set(s)
    while S:
        w = S.pop()
        for v in P[w]:
            i = 0 if w in C else delta[w]
            partial_delta = (sigma[v]/sigma[w]) * (1 + i)
            if w in C and v in C:
                continue
            else:
                delta[v] += partial_delta
        if w in C_no_s:
            GBC += delta[w]
    return GBC
