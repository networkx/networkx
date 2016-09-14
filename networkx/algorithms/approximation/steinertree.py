import networkx as nx
from itertools import combinations, chain
from networkx.utils import pairwise, not_implemented_for

__all__ = ['metric_closure', 'steiner_tree']


@not_implemented_for('directed')
def metric_closure(G, nodes, weight="weight"):
    """  Returns the sub-graph of the metric closure of the graph G induced by
        the nodes.

    Parameters:
    -----------
    G : Networkx graph

    nodes : List
            The function returns the sub-graph of metric closure induced by the
            nodes specified in this list.

    Returns:
    --------
    Metric closure of G induced by nodes.

    M : Networkx graph

    Note: If parameter nodes contain all nodes of the graph G then the function
        returns metric closure of the entire
        graph.

    """
    M = nx.Graph()

    for u, v in combinations(nodes, 2):
        distance, path = nx.single_source_dijkstra(G, u, v, weight=weight)
        M.add_edge(u, v, distance=distance[v], path=path[v])

    return M


@not_implemented_for('directed')
def steiner_tree(G, terminal_nodes, weight='weight'):
    """ Returns steiner tree of the graph induced by terminal_nodes.

    Parameters:
    -----------

    G : Networkx graph

    terminal_nodes : List
                     A list of terminal nodes for which steiner tree is to be
                     found.

    Returns:
    --------
    The steiner tree for the given terminal nodes.
    T : Networkx graph
        Steiner tree.

    Note: Steiner tree can be approximated by computing the minimum spanning
        tree of the sub-graph of the metric closure of the graph induced by the
        terminal nodes, where the metric closure of G is the complete graph in
        which each edge is weighted by the shortest path distance between the
        nodes in G.

    """
    # M is the sub-graph of the metric closure induced by the terminal nodes of
    #  G.
    M = metric_closure(G, terminal_nodes, weight=weight)
    # Use the 'distance' attribute of each edge provided by the metric closure
    # graph.
    mst_edges = nx.minimum_spanning_edges(M, weight='distance', data=True)
    # Create an iterator over each edge in each shortest path; repeats are okay
    edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
    T = G.edge_subgraph(edges)
    return T
