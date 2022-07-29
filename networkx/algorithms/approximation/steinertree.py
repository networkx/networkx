from itertools import chain

import networkx as nx
from networkx.utils import not_implemented_for, pairwise

__all__ = ["steiner_tree"]


@not_implemented_for("directed")
def steiner_tree(G, terminal_nodes, weight="weight"):
    """Return an approximation to the minimum Steiner tree of a graph.

    The minimum Steiner tree of `G` w.r.t a set of `terminal_nodes`
    is a tree within `G` that spans those nodes and has minimum size
    (sum of edge weights) among all such trees.

    This algorithm produces a tree whose weight is within a (2 - (2 / t))
    factor of the weight of the optimal Steiner tree where *t* is number of
    terminal nodes.

    Parameters
    ----------
    G : NetworkX graph

    terminal_nodes : list
         A list of terminal nodes for which minimum steiner tree is
         to be found.

    weight : If None, every edge has weight/distance/cost 1. If a string, use this edge attribute as the edge weight.
        Any edge attribute not present defaults to 1.
        If this is a function, the weight of an edge is the value returned by the function.
        The function must accept exactly three positional arguments: the two endpoints of an edge and
        the dictionary of edge attributes for that edge. The function must return a number.

    Returns
    -------
    NetworkX graph
        Approximation to the minimum steiner tree of `G` induced by
        `terminal_nodes` .

    Notes
    -----
    For multigraphs, the edge between two nodes with minimum weight is the
    edge put into the Steiner tree.


    References
    ----------
    .. [1] Steiner_tree_problem on Wikipedia.
       https://en.wikipedia.org/wiki/Steiner_tree_problem
    """
    # M is the subgraph induced by terminal_nodes with shortest corresponding pairwise paths in G.

    M = nx.Graph()
    for u_index in range(len(terminal_nodes)):
        u = terminal_nodes[u_index]

        for v_index in range(u_index+1, len(terminal_nodes)):
            v = terminal_nodes[v_index]
            dist_u_v = nx.shortest_path_length(G=G, source=u, target=v, weight=weight)
            path_u_v = nx.shortest_path(G=G, source=u, target=v, weight=weight)
            M.add_edge(u, v, distance=dist_u_v, path=path_u_v)

    # Use the 'distance' attribute of each edge provided by M.
    mst_edges = nx.minimum_spanning_edges(M, weight="distance", data=True)
    # Create an iterator over each edge in each shortest path; repeats are okay
    edges = chain.from_iterable(pairwise(d["path"]) for u, v, d in mst_edges)
    # For multigraph we should add the minimal weight edge keys
    if G.is_multigraph():
        edges = (
            (u, v, min(G[u][v], key=lambda k: G[u][v][k][weight])) for u, v in edges
        )
    T = G.edge_subgraph(edges)
    return T



