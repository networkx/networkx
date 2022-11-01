from copy import copy
from typing import Dict

import networkx as nx
from networkx.algorithms.mis import maximal_independent_set
from networkx.classes import Graph

__all__ = ["sampled_rlf"]


def sampled_rlf(G: Graph, n_searches: int = 1_000) -> Dict:
    """This is a non-deterministic approach to the Recursive
    Largest First algorithm that leverages the
    `networkx.maximal_independent_set` method, which randomly
    selects a subset of nodes in graph G such that no edges
    can be drawn between any of the selected nodes.
    This implementation will execute this method `n_searches`
    number of times and will always select the subset of nodes
    that is the largest.

    Args:
        G (Graph): an undirected networkx graph
        n_searches (int): the number of samples to take

    Returns:
        Dict: A dictionary where the key is the node and the value is the color
    """
    if not isinstance(n_searches, int):
        raise nx.NetworkXError(
            "n_searches must be an integer. " f"{n_searches} not valid."
        )
    color = {}

    temp_graph = copy(G)
    color_iter = 0

    while len(temp_graph.nodes) > 0:
        adj_dict = temp_graph.adj
        # Finding initial node
        max_len = 0
        init_node = ""
        for key in adj_dict.keys():
            cur_len = len(adj_dict.get(key))
            if cur_len >= max_len:
                init_node = key
                max_len = cur_len

        max_len = 0
        iteration = 0
        while iteration < n_searches:
            indep_nodes = maximal_independent_set(
                temp_graph, nodes=[init_node], seed=None
            )
            if len(indep_nodes) > max_len:
                max_independent_set = indep_nodes
                max_len = len(indep_nodes)
            iteration += 1

        for node in max_independent_set:
            color[node] = color_iter

        color_iter += 1
        temp_graph.remove_nodes_from(max_independent_set)

    # update the node coloring dictionary so it is ordered
    return color
