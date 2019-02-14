from itertools import combinations, chain

from networkx.utils import pairwise, not_implemented_for
import networkx as nx

__all__ = ['metric_closure', 'steiner_tree']


@not_implemented_for('directed')
def metric_closure(G, weight='weight'):
    """  Return the metric closure of a graph.

    The metric closure of a graph *G* is the complete graph in which each edge
    is weighted by the shortest path distance between the nodes in *G* .

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    NetworkX graph
        Metric closure of the graph `G`.

    """
    M = nx.Graph()

    Gnodes = set(G)

    # check for connected graph while processing first node
    all_paths_iter = nx.all_pairs_dijkstra(G, weight=weight)
    u, (distance, path, keys) = next(all_paths_iter)

    if Gnodes - set(distance):
        msg = "G is not a connected graph. metric_closure is not defined."
        raise nx.NetworkXError(msg)
    Gnodes.remove(u)
    for v in Gnodes:
        current_keys = keys[v] if keys else None
        M.add_edge(u, v, distance=distance[v], path=path[v], keys=current_keys)

    # first node done -- now process the rest
    for u, (distance, path, keys) in all_paths_iter:
        Gnodes.remove(u)
        for v in Gnodes:
            current_keys = keys[v] if keys else None
            M.add_edge(u, v, distance=distance[v], path=path[v], keys=current_keys)

    return M


@not_implemented_for('directed')
def steiner_tree(G, terminal_nodes, weight='weight', metric_closure=None):
    """ Return an approximation to the minimum Steiner tree of a graph.

    Parameters
    ----------
    G : NetworkX graph

    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    weight :
         The weight to be used for calculating the shortest path

    metric_closure:
         A precalculated metric_closure of the graph

    Returns
    -------
    NetworkX graph
        Approximation to the minimum steiner tree of `G` induced by
        `terminal_nodes` .

    Notes
    -----
    Steiner tree can be approximated by computing the minimum spanning
    tree of the subgraph of the metric closure of the graph induced by the
    terminal nodes, where the metric closure of *G* is the complete graph in
    which each edge is weighted by the shortest path distance between the
    nodes in *G* .
    This algorithm produces a tree whose weight is within a (2 - (2 / t))
    factor of the weight of the optimal Steiner tree where *t* is number of
    terminal nodes.

    """
    # M is the subgraph of the metric closure induced by the terminal nodes of
    # G.
    M = metric_closure if metric_closure else metric_closure(G, weight=weight)
    # Use the 'distance' attribute of each edge provided by the metric closure
    # graph.
    H = M.subgraph(terminal_nodes)
    mst_edges = nx.minimum_spanning_edges(H, weight='distance', data=True)

    edges = []

    if G.is_multigraph():
        edges = []

        for mst_edge in mst_edges:
            (u, v, d) = mst_edge

            for idx, pair in enumerate(pairwise(d['path'])):
                edges.append((pair[0], pair[1], d['keys'][idx]))
    else:
        # Create an iterator over each edge in each shortest path; repeats are okay
        edges = chain.from_iterable(pairwise(d['path']) for u, v, d in mst_edges)


    T = G.edge_subgraph(edges)

    return T
