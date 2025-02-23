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

    visited: set = set()
    node_data: dict = {n: {} for n in G.nodes}

    # Calculate rumor centrality for a single node
    arbitrary_start_node = list(G)[0]
    _calculate_rumor_centrality_for_single_node(
        G, arbitrary_start_node, arbitrary_start_node, visited, node_data
    )

    # Calculate rumor centrality for remaining nodes
    visited = {arbitrary_start_node}
    for neighbor in G.neighbors(arbitrary_start_node):
        _calculate_for_remaining(
            G,
            neighbor,
            node_data[arbitrary_start_node]["rumor_centrality"],
            visited,
            node_data,
        )

    return {v: node_data[v]["rumor_centrality"] for v in G.nodes}


def _calculate_rumor_centrality_for_single_node(G, v, start_node, visited, node_data):
    # Mark v as visited
    visited.add(v)

    # Collect all unvisited neighbors
    unvisited_neighbors = []
    for neighbor in G.neighbors(v):
        if neighbor not in visited:
            unvisited_neighbors.append(neighbor)

    # If v does not have unvisited neighbors, initialize v with default values
    if len(unvisited_neighbors) == 0:
        node_data[v]["subtree_size"] = 1
        node_data[v]["cumulative_prod"] = 1
        return 1, 1

    # If v has unvisited neighbors, invoke recursive call for each of them
    # and calculate cumulative sum and product
    cum_sum, cum_prod = 0, 1
    for neighbor in unvisited_neighbors:
        a, b = _calculate_rumor_centrality_for_single_node(
            G, neighbor, start_node, visited, node_data
        )
        cum_sum += a
        cum_prod *= b

    # Calculate rumor centrality for chosen root
    if v == start_node:
        node_data[v]["rumor_centrality"] = math.factorial(len(G) - 1) // cum_prod

    # Calculate v's values
    node_data[v]["subtree_size"] = cum_sum + 1
    node_data[v]["cumulative_prod"] = cum_prod * node_data[v]["subtree_size"]

    # Return v's values
    return node_data[v]["subtree_size"], node_data[v]["cumulative_prod"]


def _calculate_for_remaining(G, node, parent_rumor_centrality, visited, node_data):
    visited.add(node)
    node_data[node]["rumor_centrality"] = int(
        parent_rumor_centrality
        * node_data[node]["subtree_size"]
        / (len(G) - node_data[node]["subtree_size"])
    )

    for neighbor in G.neighbors(node):
        if neighbor not in visited:
            _calculate_for_remaining(
                G, neighbor, node_data[node]["rumor_centrality"], visited, node_data
            )
