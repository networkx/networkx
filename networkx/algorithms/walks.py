"""Functions for computing walks in a graph.

The simplest interface for computing the number of walks in a graph is
the :func:`number_of_walks` function. For more advanced usage, use the
:func:`single_source_number_of_walks` or
:func:`all_pairs_number_of_walks` functions.

"""
from itertools import starmap
from operator import eq

import networkx as nx

__all__ = [
    "all_pairs_number_of_walks",
    "number_of_walks",
    "single_source_number_of_walks",
]


def number_of_walks(G, walk_length, source=None, target=None):
    """Computes the number of walks of a particular length in the graph
    `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Neither the `source` nor the `target` nodes are required for this
    function; see the *Returns* section for more information on how
    these keyword arguments affect the output of this function.

    Parameters
    ----------
    G : NetworkX graph

    walk_length: int
        A nonnegative integer representing the length of a walk.

    source : node
        A node in the graph `G`. If not specified, the number of walks
        from all possible source nodes in the graph will be computed.

    target : node
        A node in the graph `G`. If not specified, the number of walks
        to all possible target nodes in the graph will be computed.

    Returns
    -------
    dict or int
        If both `source` and `target` are specified, the number of walks
        connecting `source` to `target` of length `walk_length` is
        returned.

        If `source` but not `target` is specified, the return value is a
        dictionary whose keys are target nodes and whose values are the
        number of walks of length `walk_length` from the source node to
        the target node.

        If `target` but not `source` is specified, the return value is a
        dictionary whose keys are source nodes and whose values are the
        number of walks of length `walk_length` from the source node to
        the target node.

        If neither `source` nor `target` are specified, this returns a
        dictionary of dictionaries in which outer keys are source nodes,
        inner keys are target nodes, and inner values are the number of
        walks of length `walk_length` connecting those nodes.

    Raises
    ------
    ValueError
        If `walk_length` is negative.
    """
    if source is None and target is None:
        return all_pairs_number_of_walks(G, walk_length)
    # Rename this function for the sake of brevity.
    single_source = single_source_number_of_walks
    if source is None and target is not None:
        # Temporarily reverse the edges of the graph *in-place*, then
        # compute the number of walks from target to the various
        # sources.
        G = G.reverse(copy=False)
        return single_source(G, walk_length, target)
    return single_source(G, walk_length, source, target=target)


def single_source_number_of_walks(G, walk_length, source, target=None):
    """Returns the number of walks from `source` to each other node in
    the graph `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : NetworkX graph

    walk_length: int
        A nonnegative integer representing the length of a walk.

    source : node
        A node in the graph `G`.

    target : node
        A node in the graph `G`. If not specified, the number of walks
        from `source` to each other node in the graph is returned.

    Returns
    -------
    dict or int
        If `target` is not specified, the return value is a dictionary
        whose keys are target nodes and whose values are the number of
        walks of length `walk_length` from the source node to the target
        node.

        If `target` is a node in the graph, this simply returns the
        number of walks from `source` to `target` in `G`.

    Raises
    ------
    ValueError
        If `walk_length` is negative.

    """
    A = nx.adjacency_matrix(G, nodelist=list(G))
    power = A**walk_length
    if target is not None:
        return power[source, target]
    result = {
        u: {v: power[u_idx, v_idx] for v_idx, v in enumerate(G)}
        for u_idx, u in enumerate(G)
    }
    return result[source]


def all_pairs_number_of_walks(G, walk_length):
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
    """
    A = nx.adjacency_matrix(G)
    power = A**walk_length
    # `u` is the source node, `v` is the target node, and `d` is the
    # number of walks with initial node `u` and terminal node `v`.
    result = {
        u: {v: power[u_idx, v_idx] for v_idx, v in enumerate(G)}
        for u_idx, u in enumerate(G)
    }
    return result
