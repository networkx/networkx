import warnings
from collections import defaultdict, deque

import networkx as nx


def pll_preprocess(G):
    """Preprocess the directed graph for the PLL reachability algorithm.

    This function computes the labels needed for the reachability
    queries using the PLL (Path Length Limiting) method.

    Parameters
    ----------
    G : networkx.DiGraph
        The directed graph for which to preprocess reachability.

    Returns
    -------
    labels_out : defaultdict(dict)
        A dictionary containing the reachability information for each node,
        where keys are nodes and values are dictionaries mapping target nodes
        to their respective distances.
        Traversal algorithm BFS is used to get the reachability information of each node.
        Prunning is applied where neccessary during the traversal to shorten the dictionary's size

    labels_in : defaultdict(dict)
        A dictionary containing the reverse reachability information for each node.
    """
    degrees = [(v, (G.in_degree(v) + 1) * (G.out_degree(v) + 1)) for v in G.nodes()]
    sorted_vertices = sorted(degrees, key=lambda x: x[1], reverse=True)
    vertex_order = [v for v, d in sorted_vertices]

    L_out = defaultdict(dict)
    L_in = defaultdict(dict)
    rank = {v: i for i, v in enumerate(vertex_order)}

    for v in vertex_order:
        forward_bfs(G, v, rank, L_out, L_in)
        backward_bfs(G, v, rank, L_out, L_in)

    return L_out, L_in


def forward_bfs(G, source, rank, L_out, L_in):
    visited = set()
    queue = deque([(source, 0)])
    while queue:
        u, d = queue.popleft()
        if u in visited:
            continue
        visited.add(u)

        # Pruning: Skip u if it has already been processed
        if rank[u] < rank[source]:
            continue

        if source in L_in[u]:  # Pruning condition
            continue

        L_out[source][u] = d

        for neighbor in G.successors(u):
            if neighbor not in visited:
                queue.append((neighbor, d + 1))


def backward_bfs(G, source, rank, L_out, L_in):
    visited = set()
    queue = deque([(source, 0)])
    while queue:
        u, d = queue.popleft()
        if u in visited:
            continue
        visited.add(u)

        # Pruning: Skip u if it has already been processed
        if rank[u] < rank[source]:
            continue

        if source in L_out[u]:  # Pruning condition
            continue

        L_in[source][u] = d

        for neighbor in G.predecessors(u):
            if neighbor not in visited:
                queue.append((neighbor, d + 1))


def bfs_check(G, source, target):
    visited = set()
    queue = deque([source])
    while queue:
        u = queue.popleft()
        if u == target:
            return True
        if u in visited:
            continue
        visited.add(u)
        for neighbor in G.successors(u):
            if neighbor not in visited:
                queue.append(neighbor)
    return False


def pll_has_path(G, source, target, labels_in, labels_out):
    """Check if a path exists between two nodes in a directed graph using PLL reachability.

    This function uses the preprocessed labels from `pll_preprocess` to
    determine if a path exists between the source and target nodes. If the
    labels indicate a direct connection, it returns True; otherwise, it falls
    back to a breadth-first search to check for connectivity.

    Parameters
    ----------
    G : networkx.DiGraph
        The directed graph in which to check for a path.

    source : node
        The starting node for the path.

    target : node
        The ending node for the path.

    labels_in : defaultdict(dict)
        The reverse reachability labels obtained from `pll_preprocess`.

    labels_out : defaultdict(dict)
        The reachability labels obtained from `pll_preprocess`.

    Returns
    -------
    bool
        True if a path exists from source to target; False otherwise.

    Notes
    -----
    If the graph is empty, or if the source or target nodes are None,
    the function returns False.
    If initial condition returns False, further search is being done using BFS to determine that the result is a True Negative.

    """
    if nx.is_empty(G):
        return False
    if source is None:
        return False
    if target is None:
        return False
    if target in labels_out[source] or source in labels_in[target]:
        return True

    return bfs_check(G, source, target)
