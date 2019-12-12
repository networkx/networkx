"""Approximate solutions to Traveling Salesman Problems

The Christofides algorithm provides a 3/2-approximation of TSP.
"""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["christofides", "traveling_salesman_problem"]


def _shortcutting(circuit):
    nodes = []
    for u, v in circuit:
        if v in nodes:
            continue
        yield (nodes[-1] if nodes else u, v)
        if not nodes:
            nodes.append(u)
        nodes.append(v)
    yield(nodes[-1], nodes[0])


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def christofides(G, weight='weight', tree=None):
    """Approximate a solution of the traveling salesman problem

    Compute a 3/2-approximation of the traveling salesman problem
    in a complete undirected graph using Christofides [1] algorithm.

    Parameters
    ----------
    G : Graph
      Undirected complete graph

    weight : string, optional (default='weight')
      Edge data key corresponding to the edge weight.
      If key not found, uses 1 as weight.

    tree : NetworkX graph or None (default: computed)
      A minimum spanning tree of G. Or, if None, the minimum spanning
      tree is computed using :func:`networkx.minimum_spanning_tree`

    Returns
    -------
    Generator of edges forming a 3/2-approximation of the minimal
    Hamiltonian cycle.

    References
    ----------
    .. [1] Christofides, Nicos. "Worst-case analysis of a new heuristic for
      the travelling salesman problem." No. RR-388. Carnegie-Mellon Univ
      Pittsburgh Pa Management Sciences Research Group, 1976.
    """
    # Check that G is a complete graph
    for e in nx.selfloop_edges(G):
        raise ValueError("Christofides algorithm does not allow selfloops")
    n = len(G)
    m = G.size()
    if (n * (n - 1) // 2) != m:
        raise ValueError("Christofides algorithm needs a complete graph")

    if tree is None:
        tree = nx.minimum_spanning_tree(G, weight=weight)
    L = nx.Graph(G)
    L.remove_nodes_from([v for v, degree in tree.degree if not (degree % 2)])
    MG = nx.MultiGraph()
    MG.add_edges_from(tree.edges)
    edges = nx.min_weight_matching(L, maxcardinality=True, weight=weight)
    MG.add_edges_from(edges)
    return _shortcutting(nx.eulerian_circuit(MG))


@not_implemented_for('directed')
def traveling_salesman_problem(G, nodes, weight=None, cycle=True):
    """Find the shortest path in G connecting specified nodes

    This function uses the Christofides algorithm to provide an
    approximate solution to the traveling salesman problem.

    This function proceeds in two steps. First, it creates a complete
    graph using the all-pairs shortest_paths between nodes in `nodes`.
    Edges weights in the new graph are the lengths of the paths
    between each pair of nodes in the original graph.
    Second, the Christofides algorithm is used to approximate
    the minimal hamiltonian cycle on this new graph.
    The hamiltonian cycle is returned by `christofides`.

    This function then turns that hamiltonian cycle through `nodes`
    into a cycle on the original graph using shortest paths between
    nodes. It then returns the minimal cycle through `nodes` in `G`.
    If `cycle is False`, the biggest weight is removed to make a path.

    Parameters
    ----------
    G : NetworkX graph
      Undirected possibly weighted graph

    nodes : sequence of nodes
      sequence (list, set, etc) of nodes to visit

    weight : string optional (default=None)
      The name of the edge attribute to use for edge weights.
      Edge weights default to 1 if the weight attribute is not present.
      If None, every edge has weight 1.

    cycle : bool (default: True)
      Indicates whether a cycle should be returned, or a path
      Note: the systel is the approximate minimal cycle.
      The path simply removes the biggest edge in that cycle.

    Returns
    -------
    list of nodes in `G` along a path with a
    3/2-approximation of the minimal path through `nodes`.
    """
    dist = {}
    path = {}
    for n, (d, p) in nx.all_pairs_dijkstra(G, weight=weight):
        dist[n] = d
        path[n] = p

    GG = nx.Graph()
    for u in nodes:
        for v in nodes:
            if u == v:
                continue
            GG.add_edge(u, v, weight=dist[u][v])
    best_GG = list(christofides(GG, weight=weight))

    if not cycle:
        # find and remove the biggest edge
        biggest_edge = None
        length_biggest = float('-inf')
        for edge in best_GG:
            u, v = edge[:2]
            if dist[u][v] > length_biggest:
                biggest_edge = edge
                length_biggest = dist[u][v]
        pos = best_GG.index(biggest_edge)
        best_GG = best_GG[pos + 1:] + best_GG[:pos]

    best_path = []
    for u, v in best_GG:
        best_path.extend(path[u][v][:-1])
    best_path.append(v)
    return best_path
