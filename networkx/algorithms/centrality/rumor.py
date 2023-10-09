import math

import networkx as nx
from networkx.utils.decorators import not_implemented_for

__all__ = ["rumor_centrality"]


@not_implemented_for("directed")
def rumor_centrality(G):
    """Compute the rumor centrality for nodes.

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

    Notes
    -----
    Rumor centrality was introduced by Shah & Zaman [1]_ for rumor source detection.

    .. [1] Shah, Devavrat, and Tauhid Zaman. "Rumor centrality: a universal source detector." In Proceedings of the
    12th ACM SIGMETRICS/PERFORMANCE joint international conference on Measurement and Modeling of Computer Systems,
    pp. 199-210. 2012.

    """

    if len(G) == 0:
        raise nx.NetworkXPointlessConcept(
            "cannot compute centrality for the null graph"
        )

    if G.is_multigraph():
        raise NotImplementedError("multigraphs are not supported by this algorithm")

    if G.is_directed():
        raise NotImplementedError("directed graphs are not supported by this algorithm")

    cycles = list(nx.simple_cycles(G))
    if len(cycles) > 0:
        raise nx.NetworkXUnfeasible(
            "rumor centrality does not work for graphs with cycles"
        )

    # Create copy to be able to use node properties
    H = G.copy()
    set_visited_to_false(H)

    # Calculate rumor centrality for a single vertex
    arbitrary_start_vertex = list(H)[0]
    calculate_rumor_centrality_for_single_vertex(
        H, arbitrary_start_vertex, arbitrary_start_vertex
    )

    # Calculate rumor centrality for remaining vertices
    set_visited_to_false(H)
    H.nodes[arbitrary_start_vertex]["visited"] = True
    for neighbor in H.neighbors(arbitrary_start_vertex):
        calculate_for_remaining(
            H, neighbor, H.nodes[arbitrary_start_vertex]["rumor_centrality"]
        )

    return {v: H.nodes[v]["rumor_centrality"] for v in H.nodes}


def calculate_rumor_centrality_for_single_vertex(G, v, start_vertex):
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
        a, b = calculate_rumor_centrality_for_single_vertex(G, neighbor, start_vertex)
        cum_sum += a
        cum_prod *= b

    # Calculate rumor centrality for chosen root
    if v == start_vertex:
        G.nodes[v]["rumor_centrality"] = math.factorial(len(G) - 1) // cum_prod

    # Calculate v's values
    G.nodes[v]["subtree_size"] = cum_sum + 1
    G.nodes[v]["cumulative_prod"] = cum_prod * G.nodes[v]["subtree_size"]

    # Return v's values
    return G.nodes[v]["subtree_size"], G.nodes[v]["cumulative_prod"]


def set_visited_to_false(G):
    for node in G.nodes:
        G.nodes[node]["visited"] = False


def calculate_for_remaining(G, vertex, parent_rumor_centrality):
    G.nodes[vertex]["visited"] = True
    G.nodes[vertex]["rumor_centrality"] = int(
        parent_rumor_centrality
        * G.nodes[vertex]["subtree_size"]
        / (len(G) - G.nodes[vertex]["subtree_size"])
    )

    for neighbor in G.neighbors(vertex):
        if not G.nodes[neighbor]["visited"]:
            calculate_for_remaining(G, neighbor, G.nodes[vertex]["rumor_centrality"])
