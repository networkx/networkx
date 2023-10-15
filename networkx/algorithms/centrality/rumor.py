import math

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["rumor_centrality"]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def rumor_centrality(G: nx.Graph):
    """Compute the rumor centrality for nodes.

    Rumor centrality is a rumor source detector which uses the network's
    topology to estimate which (single) node is the most likely source of the
    rumor. In some cases (cf. [1]) it is the maximum likelihood estimator.

    Rumor centrality is a centrality that has been developed to estimate the
    source of some kind of information (e.g., a rumor) in an information
    diffusion network.

    In comparison to many other centralities (e.g., degree, closeness,
    betweenness), rumor centrality works only on tree graphs. For graphs with
    cycles, rumor centrality is usually applied to the BFS tree of the graph.

    Parameters
    ----------
    G : graph
      A networkx graph

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with degree centrality as the value.

    Raises
    ------
    NetworkXPointlessConcept
        If the graph G is the null graph.

    NetworkXNotImplemented
        If the graph is a multigraph, directed, or contains cycles.

    Notes
    -----
    Rumor centrality was introduced by Shah & Zaman [1]_ for rumor source
    detection.

    .. [1] Shah, Devavrat, and Tauhid Zaman. "Rumor centrality: a universal
    source detector." In Proceedings of the 12th ACM SIGMETRICS/PERFORMANCE
    joint international conference on Measurement and Modeling of Computer
    Systems, pp. 199-210. 2012.
    """

    if not nx.is_tree(G):
        raise nx.NetworkXNotImplemented("graph must be a tree")

    # Create copy to be able to use node properties
    H = G.copy()
    _set_visited_to_false(H)

    # Calculate rumor centrality for a single node
    arbitrary_start_node = list(H)[0]
    _calculate_rumor_centrality_for_single_node(
        H, arbitrary_start_node, arbitrary_start_node
    )

    # Calculate rumor centrality for remaining vertices
    _set_visited_to_false(H)
    H.nodes[arbitrary_start_node]["visited"] = True
    for neighbor in H.neighbors(arbitrary_start_node):
        _calculate_for_remaining(
            H, neighbor, H.nodes[arbitrary_start_node]["rumor_centrality"]
        )

    return {v: H.nodes[v]["rumor_centrality"] for v in H.nodes}


def _calculate_rumor_centrality_for_single_node(G, v, node):
    # Mark v as visited
    G.nodes[v]["visited"] = True

    # Collect all unvisited neighbors
    unvisited_neighbors = []
    for neighbor in G.neighbors(v):
        if not G.nodes[neighbor]["visited"]:
            unvisited_neighbors.append(neighbor)

    # If v does not have unvisited neighbors, initialize v with default values
    if len(unvisited_neighbors) == 0:
        G.nodes[v]["subtree_size"] = 1
        G.nodes[v]["cumulative_prod"] = 1
        return 1, 1

    # If v has unvisited neighbors, invoke recursive call for each of them
    # and calculate cumulative sum and product
    cum_sum, cum_prod = 0, 1
    for neighbor in unvisited_neighbors:
        a, b = _calculate_rumor_centrality_for_single_node(G, neighbor, node)
        cum_sum += a
        cum_prod *= b

    # Calculate rumor centrality for chosen root
    if v == node:
        G.nodes[v]["rumor_centrality"] = math.factorial(len(G) - 1) // cum_prod

    # Calculate v's values
    G.nodes[v]["subtree_size"] = cum_sum + 1
    G.nodes[v]["cumulative_prod"] = cum_prod * G.nodes[v]["subtree_size"]

    # Return v's values
    return G.nodes[v]["subtree_size"], G.nodes[v]["cumulative_prod"]


def _set_visited_to_false(G):
    for node in G.nodes:
        G.nodes[node]["visited"] = False


def _calculate_for_remaining(G, node, parent_rumor_centrality):
    G.nodes[node]["visited"] = True
    G.nodes[node]["rumor_centrality"] = int(
        parent_rumor_centrality
        * G.nodes[node]["subtree_size"]
        / (len(G) - G.nodes[node]["subtree_size"])
    )

    for neighbor in G.neighbors(node):
        if not G.nodes[neighbor]["visited"]:
            _calculate_for_remaining(G, neighbor, G.nodes[node]["rumor_centrality"])
