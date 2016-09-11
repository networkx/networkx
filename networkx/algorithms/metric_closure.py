import networkx as nx
from itertools import combinations
from networkx.utils import not_implemented_for


@not_implemented_for('directed')
def metric_closure(G, weight="weight"):
    """ Returns the metric closure of a graph.
    Parameters:
    -----------
    G : Networkx graph
    
    Returns:
    --------
    Metric closure of a graph.
    Return type:
    Networkx graph.

    Note: The metric closure of a graph G is the complete graph in which each edge is weighted by the shortest path
    distance between the nodes in G.

    """
    # metric closure of G.
    M = nx.Graph()
    for u, v in combinations(G, 2):
        # calculate shortest path and distance between all pairs of nodes.
        distance, path = nx.single_source_dijkstra(G, u, v, weight=weight)
        M.add_edge(u, v, distance=distance[v], path=path[v])

    return M

