"""Function for computing walks in a graph.
"""
from itertools import starmap
from operator import eq

import networkx as nx

__all__ = ["number_of_walks"]


def number_of_walks(G, walk_length):
    """Returns the number of walks connecting each pair of nodes in
    `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : NetworkX graph

    walk_length : int
        A nonnegative integer representing the length of a walk.

    Returns
    -------
    dict
        A dictionary of dictionaries in which outer keys are source
        nodes, inner keys are target nodes, and inner values are the
        number of walks of length `walk_length` connecting those nodes.

    Raises
    ------
    ValueError
        If `walk_length` is negative

    Examples
    --------

    >>> G = nx.DiGraph([(0, 1), (1, 2)])
    >>> nx.number_of_walks(G, 2)
    {0: {0: 0, 1: 0, 2: 1}, 1: {0: 0, 1: 0, 2: 0}, 2: {0: 0, 1: 0, 2: 0}}

    You can also reach number of walks from a specific source node using the returned dictionary.
    For example, number of walks of length 1 from node 0 can be found as follows:

    >>> walks = nx.number_of_walks(G, 1)
    >>> walks[0]
    {0: 0, 1: 1, 2: 0}

    Similarly, a target node can also be specified:

    >>> walks[0][1]
    1

    """
    A = nx.adjacency_matrix(G)
    power = A**walk_length
    result = {
        u: {v: power[u_idx, v_idx] for v_idx, v in enumerate(G)}
        for u_idx, u in enumerate(G)
    }
    return result
