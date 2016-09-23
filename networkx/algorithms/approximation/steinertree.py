from itertools import combinations, chain

from networkx.utils import pairwise, not_implemented_for
import networkx as nx

__all__ = ['metric_closure', 'steiner_tree']


@not_implemented_for('directed')
def metric_closure(G, weight='weight'):
    """  Return the metric closure of a graph.

    The metric closure of a graph G is the complete graph in which each edge is
    weighted by the shortest path distance between the nodes in G.

    Parameters
    ----------
    G : Networkx graph

    Returns
    -------
    Networkx graph
        Metric closure of the graph G.

    """
    M = nx.Graph()

    for u, v in combinations(G, 2):
        distance, path = nx.single_source_dijkstra(G, u, v, weight=weight)
        M.add_edge(u, v, distance=distance[v], path=path[v])

    return M


@not_implemented_for('directed')
def steiner_tree(G, terminal_nodes, weight='weight'):
    """ Returns an approximation to minimum steiner tree of the graph G.

    Parameters
    ----------
    G : Networkx graph

    terminal_nodes : List
                     A list of terminal nodes for which minimum steiner tree is
                     to be found.

    Returns
    -------
    Networkx graph
        Approximation to the minimum steiner tree of G induced by
        terminal_nodes.

    Notes
    -----

        Steiner tree can be approximated by computing the minimum spanning
        tree of the subgraph of the metric closure of the graph induced by the
        terminal nodes, where the metric closure of G is the complete graph in
        which each edge is weighted by the shortest path distance between the
        nodes in G.
        This algorithm produces a tree whose weight is within a (2 - (2 / t))
        factor of the weight of the optimal Steiner tree.

    """
    # M is the subgraph of the metric closure induced by the terminal nodes of
    #  G.
    M = metric_closure(G, weight=weight)
    # Use the 'distance' attribute of each edge provided by the metric closure
    # graph.
    H = M.subgraph(terminal_nodes)
    mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)
    # Create an iterator over each edge in each shortest path; repeats are okay
    edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)
    T = G.edge_subgraph(edges)
    return T
