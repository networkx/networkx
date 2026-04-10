import math

import networkx as nx
from networkx.exception import NetworkXError


def karp(G, source=None, weight="weight"):
    """
    Finds the minimum mean negative cycle using Karp's Algorithm.

    1. Preprocesses MultiDiGraphs to simple DiGraphs (keeping min weight).
    2. Uses Dynamic Programming to find shortest paths of exact lengths.
    3. Applies Karp's formula to find the minimum mean value.
    4. Traces back through DP layers to recover the exact cycle nodes.
    """

    # STEP 1: PREPROCESS -------------------------------------------------------
    # Cycle-cancelling residual graphs are MultiDiGraphs
    # Karp's DP requires a simple DiGraph where we use the cheapest edge
    if not isinstance(G, nx.DiGraph | nx.MultiDiGraph):
        raise TypeError("Karp requires a directed graph")

    if G.is_multigraph():
        S = nx.DiGraph()
        for u, v, data in G.edges(data=True):
            w = data.get(weight, 0)
            if S.has_edge(u, v):
                # Save only one edge per direction between two nodes
                # Choose the cheapest edge
                if w < S[u][v][weight]:
                    S[u][v][weight] = w
            else:
                S.add_edge(u, v, **{weight: w})
        G = S

    # Initialization for dynamic programming
    nodes = list(G.nodes())
    n = len(nodes)
    if n == 0:
        raise nx.NetworkXError("Empty graph")

    idx = {v: i for i, v in enumerate(nodes)}  # Index mapping: node → int

    # dp[k][v] = min cost of walk of length k ending at v
    dp = [[math.inf] * n for _ in range(n + 1)]
    # parent[k][v] = the node u that preceded v in a path of length k
    # Compute walks of length up to n: any cycle must repeat within n nodes
    parent = [[None] * n for _ in range(n + 1)]

    # Virtual source: initialize all nodes at distance 0
    # Allows detecting cycles anywhere in the graph
    for v in range(n):
        dp[0][v] = 0

    # STEP 2: DYNAMIC PROGRAMMING ----------------------------------------------
    # Calculate shortest paths for every length k from 1 to n
    for k in range(1, n + 1):
        # Iterate over all directed edges (u → v)
        for u, v, data in G.edges(data=True):
            w = data[weight]
            # Convert node labels to integer indices for DP table access
            ui, vi = idx[u], idx[v]
            # If extending the cheapest (k−1)-edge walk ending at u via edge u→v
            # yields a cheaper k-edge walk ending at v, update the DP value
            if dp[k - 1][ui] + w < dp[k][vi]:
                dp[k][vi] = dp[k - 1][ui] + w
                parent[k][vi] = u

    # STEP 3: KARP'S MIN-MAX FORMULA -------------------------------------------
    mu = math.inf  # Initialize the minimum mean cycle cost to infinity
    v_star = None  # Will store a node that lies on the minimum mean cycle

    # Iterate over every node to consider cycles ending at that node
    for v in range(n):
        if dp[n][v] == math.inf:
            # Skip nodes that are unreachable in a walk of length n
            continue

        # max_k [(dp[n][v] - dp[k][v]) / (n - k)]
        max_avg = -math.inf
        for k in range(n):
            if dp[k][v] != math.inf:
                avg = (dp[n][v] - dp[k][v]) / (n - k)
                if avg > max_avg:
                    max_avg = avg

        if max_avg < mu:
            mu = max_avg
            v_star = v

    # STEP 4: TERMINATION CHECK ------------------------------------------------
    # mu < 0 indicates a negative mean cycle exists
    # Use small epsilon to handle floating point precision issues
    if v_star is None or mu >= -1e-11:
        raise nx.NetworkXError("No negative mean cycle found")

    # STEP 5: ROBUST CYCLE RECONSTRUCTION --------------------------------------
    # We trace the path back from the n-th layer to find the repeated nodes
    curr = nodes[v_star]
    path = []
    for k in range(n, -1, -1):
        path.append(curr)
        curr = parent[k][idx[curr]]
        if curr is None:
            break

    path.reverse()

    # Identify the actual cycle within the path (remove the "tail")
    seen = {}
    for i, node in enumerate(path):
        if node in seen:
            # Return cycle including the closing node for the backbone
            return path[seen[node] : i + 1]
        seen[node] = i

    raise nx.NetworkXError("Failed to reconstruct cycle")
