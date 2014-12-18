# walks.py - functions for computing walks in a graph
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for computing walks in a graph.

The simplest interface for computing the number of walks in a graph is
the :func:`number_of_walks` function. For more advanced usage, use the
:func:`single_source_number_of_walks` or
:func:`all_pairs_number_of_walks` functions.

"""
from collections import Counter
from collections import deque

import networkx as nx

__all__ = ['all_pairs_number_of_walks', 'number_of_walks',
           'single_source_number_of_walks']


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
    if source is None and target is not None:
        # Temporarily reverse the edges of the graph *in-place*, then
        # compute the number of walks from target to the various
        # sources.
        with nx.utils.reversed(G):
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
    if walk_length < 0:
        raise ValueError('walk length must be a positive integer')
    # Create a counter to store the number of walks of length
    # `walk_length`. Ensure that even unreachable vertices have count zero.
    result = Counter({v: 0 for v in G})
    queue = deque()
    queue.append((source, 0))
    # TODO We could reduce the number of iterations in this loop by performing
    # multiple `popleft()` calls at once, since the queue is partitioned into
    # slices in which all enqueued vertices in the slice are at the same
    # distance from the source. In other words, if we keep track of the
    # *number* of vertices at each distance, we could just immediately dequeue
    # all of those vertices.
    while queue:
        (u, distance) = queue.popleft()
        if distance == walk_length:
            result[u] += 1
        else:
            # Using `nx.edges()` accounts for multiedges as well.
            queue.extend((v, distance + 1) for u_, v in nx.edges(G, u))
    if target is None:
        # Return the result as a true dictionary instead of a Counter object.
        return dict(result)
    return result[target]


#: Rename this function for the sake of brevity in this module.
single_source = single_source_number_of_walks


def all_pairs_number_of_walks(G, walk_length):
    """Returns the number of walks connecting each pair of nodes in
    `G`.

    A *walk* is a sequence of nodes in which each adjacent pair of nodes
    in the sequence is adjacent in the graph.

    Parameters
    ----------
    G : NetworkX graph

    walk_length: int
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
        If `walk_length` is negative.

    """
    # TODO This algorithm can be trivially parallelized.
    return {v: single_source_number_of_walks(G, walk_length, v) for v in G}
