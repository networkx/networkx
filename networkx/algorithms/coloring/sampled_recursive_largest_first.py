from copy import copy
from typing import Dict

import networkx as nx
from networkx.algorithms.mis import maximal_independent_set
from networkx.classes import Graph

__all__ = ["sampled_rlf_color"]


def sampled_rlf_color(G: Graph, n_searches: int = 1_000) -> Dict:
    """Color a graph using variant of Recursive Largest First algorithm.

    Attempts to color a graph using as few colors as possible, where no
    neighbours of a node can have same color as the node itself. The
    number `n_searches` is the number of maximal independent sets
    sampled. Of all the maximal independent sets, the set with the
    greatest number of nodes is selected to be colored. This is a
    non-deterministic approach. The pseudo-code for this algorithm
    is as follows:

    1. Let `G` be an undirected graph with nodes `n_1 ... n_n`
    2. Select the node from `n_1 ... n_n` with the highest degree.
    If there are multiple, just select the first one.
    3. Sample `n_searches` maximal idependent sets using
    `nx.maximal_independent_set()` and choose the set with
    the greatest number of nodes, called `n_max`.
    4. Assign `n_max` to the same color.
    5. Remove `n_max` from the graph.
    6. Repeat steps 2 through 5 until there are no more nodes
    in the graph.

    Parameters
    ----------
    G : NetworkX graph

    n_searches : int
       the number of maximal independent set samples to take
       from graph G

    Returns
    -------
    A dictionary with keys representing nodes and values representing
    corresponding coloring.

    Examples
    --------
    >>> G = nx.Graph([(0, 1), (1, 2), (1, 3)])
    >>> d = nx.coloring.sampled_rlf_color(G, n_searches=1_000)
    >>> print(d)
    {0: 1, 1: 0, 2: 1, 3: 1}

    Raises
    ------
    NetworkXNotImplemented
        If ``G`` is not an undirected graph

    NetworkXError
        If ``n_searches`` is not an integer

    References
    ----------
    .. [1] 'Recursive Largest First Algorithm.'
       Wikipedia. Wikimedia Foundation, January 15, 2022.
       https://en.wikipedia.org/wiki/Recursive_largest_first_algorithm#cite_ref-:1_2-0.
    """
    if not isinstance(n_searches, int):
        raise nx.NetworkXError(
            "n_searches must be an integer. " f"{n_searches} not valid."
        )

    if not isinstance(G, Graph):
        raise nx.NetworkXNotImplemented(
            "G must be an undirected networkx graph. " f"{G} not valid."
        )
    color = {}

    temp_graph = copy(G)
    color_iter = 0

    while len(temp_graph.nodes) > 0:
        # finding node with the highest degree
        init_node = sorted(G.degree, key=lambda x: x[1], reverse=True)[0][0]

        # iteratively finding maximal independent set, assigning color
        # then removing the maximal independent set from the graph
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
