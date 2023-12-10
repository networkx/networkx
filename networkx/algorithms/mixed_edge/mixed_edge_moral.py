import itertools

import networkx as nx

__all__ = ["mixed_edge_moral_graph"]


def mixed_edge_moral_graph(
    G,
    directed_edge_name="directed",
    undirected_edge_name="undirected",
    bidirected_edge_name="bidirected",
):
    """Return the moral graph from an ancestral graph.

    An ancestral graph is a mixed edge graph with possiblye directed,
    bidirected, and undirected edges that results when marginalizing one
    or more vertices from a directed acyclic graph. It is commonly used in
    statistical and Markov modeling.

    The moral graph is the undirected graph that results from converting
    all existing edges to undirected edges and adding an undirected edge
    between all nodes that have a common child. For example, if we have
    two nodes, ``u`` and ``v`` and there exists a v-structure
    ``u -> w <- v``, where ``u`` and ``v`` are not adjacent, then ``u -- v``
    edge is added to the moral graph. See [2]_ for more details.

    The algorithm runs in :math:`O(|V|^2)` [1]_.

    Parameters
    ----------
    G : mixed-edge-graph
        Mixed edge causal graph.
    directed_edge_name : str
        Name of the directed edge, default is directed.
    bidirected_edge_name : str
        Name of the bidirected edge, default is bidirected.
    undirected_edge_name : str
        Name of the undirected edge, default is undirected.

    Returns
    -------
    G_a : nx.Graph
        Moralized graph

    References
    ----------
    .. [1] B. van der Zander, M. Liśkiewicz, and J. Textor, “Separators and Adjustment
       Sets in Causal Graphs: Complete Criteria and an Algorithmic Framework,” Artificial
       Intelligence, vol. 270, pp. 1–40, May 2019, doi: 10.1016/j.artint.2018.12.006.
    .. [2] https://en.wikipedia.org/wiki/Moral_graph
    """

    has_undirected = undirected_edge_name in G.edge_types
    if has_undirected:
        G_undirected = G.get_graphs(edge_type=undirected_edge_name)
    else:
        G_undirected = nx.DiGraph()
        G_undirected.add_nodes_from(G)
    has_directed = directed_edge_name in G.edge_types
    if has_directed:
        G_directed = G.get_graphs(edge_type=directed_edge_name)
    else:
        G_directed = nx.DiGraph()
        G_directed.add_nodes_from(G)
    has_bidirected = bidirected_edge_name in G.edge_types
    if has_bidirected:
        G_bidirected = G.get_graphs(edge_type=bidirected_edge_name)
    else:
        G_bidirected = nx.Graph()
        G_bidirected.add_nodes_from(G)

    G_a = nx.Graph()
    G_a = nx.compose(G_a, G_undirected.to_undirected())
    G_a = nx.compose(G_a, G_directed.to_undirected())
    G_a = nx.compose(G_a, G_bidirected.to_undirected())

    for component in nx.connected_components(G_bidirected):
        for u, v in itertools.combinations(component, 2):
            G_a.add_edge(u, v)
        all_parents = {
            parent for node in component for parent in G_directed.predecessors(node)
        }
        for node in component:
            for parent in all_parents - {node}:
                G_a.add_edge(node, parent)

    return G_a
