# fvs.py - approximate feedback vertex set algorithm
#
# Copyright 2004-2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Approximate feedback vertex set algorithm."""
from __future__ import division
from collections import Counter
from collections import deque

import networkx as nx
from networkx.utils import arbitrary_element
from networkx.utils import not_implemented_for

__all__ = ['min_feedback_vertex_set']


def paths_of_degree_2(G):
    """Yield maximal paths in the graph in which each node is of degree two.

    `G` is an undirected graph. Each path yielded by this function is a
    list of length at least two in which each node has degree two and
    the two endpoints have no further degree two neighbors (i.e., the
    path is maximal in the set of paths of degree two).

    The worst-case running time of this function is :math:`O(n)`, where
    *n* is the number of nodes in the graph, ignoring polylogarithmic
    factors.

    """
    nodes = {v for v, d in G.degree() if d == 2}
    while nodes:
        # Choose an arbitrary node as the "start" node, i.e., a
        # nonterminal node in a path.
        start = nodes.pop()
        path = deque([start])
        left, right = G[start]

        # Build the path out from the starting node in both the left and
        # the right directions. For each direction, we do this by
        # repeatedly appending the next neighbor to the appropriate side
        # of the path.
        #
        # TODO The two iterations of this loop can be performed in parallel.
        for next_, append in [(left, path.appendleft), (right, path.append)]:
            prev = start
            while next_ in nodes:
                nodes.remove(next_)
                append(next_)
                # G[next_] gives us the two neighbors of next_, but we
                # don't which neighbor is the one we have already
                # visited and which is the new neighbor. We do a quick
                # check to determine which is which.
                u, v = G[next_]
                if u == prev:
                    next_, prev = v, next_
                else:
                    next_, prev = u, next_
        # For the purposes of this function, we ignore any path of
        # length one since it cannot be part of a semidisjoint cycle.
        if len(path) > 1:
            yield list(path)


def semidisjoint_cycles(G):
    """Yield all semidisjoint cycles in a graph.

    A *semidisjoint cycle* is a cycle which each node is of degree two
    with at most one exception.

    `G` is an undirected graph. This function yields a list of nodes
    representing a semidisjoint cycle in the graph.

    The worst-case running time of this function is :math:`O(n)`, where
    *n* is the number of nodes in `G`, ignoring polylogarithmic factors.

    """
    for path in paths_of_degree_2(G):
        # Since we are guaranteed that each path is of length at least
        # two, these lines will not cause an index out of bounds error.
        u, u_parent = path[:2]
        w_parent, w = path[-2:]

        # Since each node in the path has degree two, each endpoint has
        # exactly two neighbors, one of which is its "medial" neighbor
        # in the path and one of which is not. Determine which neighbor
        # is not the medial one.
        x, y = G[u]
        if x == u_parent:
            u_next = y
        else:
            u_next = x
        x, y = G[w]
        if x == w_parent:
            w_next = y
        else:
            w_next = x

        # It could be the case that u_next == w and w_next == u, in
        # which case the path is itself a cycle disjoint from any other
        # nodes in the graph (if there are any).
        if u_next == w and w_next == u:
            yield path
        # Otherwise, if the neighbors are equal, then the two endpoints
        # have a common neighbor and appending the common neighbor to
        # the path yields a semidisjoint cycle.
        elif u_next == w_next:
            yield [u_next] + path
        else:
            # At this point, the path is not a semidisjoint cycle, so we
            # do nothing.
            pass


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def min_feedback_vertex_set(G, weight='weight'):
    """Return an approximate minimum feedback vertex set for a weighted graph.

    Parameters
    ----------
    G : undirected graph

    weight : string (default 'weight')
        The node attribute that gives the weight of the node; if the
        attribute does not exist for a node, it is assumed to have
        weight one.

    Returns
    -------
    set
        A set of nodes representing a feedback vertex.

    Raises
    ------
    NetworkXNotImplemented
        If `G` is directed or a multigraph.

    Notes
    -----
    This algorithm is from [1]_. It returns a feedback vertex set whose
    total weight is at most twice the weight of the true minimum
    feedback vertex set. The worst-case running time of the algorithm is
    :math:`O(n^2)`, where *n* is the number of nodes in the graph,
    ignoring polylogarithmic factors.

    References
    ----------
    .. [1] Bafna, Vineet, Piotr Berman, and Toshihiro Fujito.
       "A 2-approximation algorithm for the undirected
       feedback vertex set problem." *SIAM Journal on Discrete Mathematics*
       12.3 (1999): 289-297. <https://dx.doi.org/10.1137/S0895480196305124>

    """

    def move_and_cleanup(G, F, weights, stack=None):
        """Move all nodes with weight zero from G to F.

        Each node of weight zero moved from `G` to `F` is recorded in
        `stack`, if given. After removing the nodes of weight zero from
        `G` and adding them to `F`, this function modifies `G` to be its
        two-core. This also clears the nodes of weight zero from the
        `weights` dictionary as well.

        """
        # Move all weight zero nodes from G to F, pushing each onto the
        # stack if necessary.
        weight_zero_nodes = {v for v in G if weights[v] == 0}
        G.remove_nodes_from(weight_zero_nodes)
        F |= weight_zero_nodes
        if stack is not None:
            stack.extend(weight_zero_nodes)
        # Compute the two-core and remove each node not in the two-core
        # from the dictionary of weights.
        before = set(G)
        G = nx.k_core(G, k=2)
        for v in before - set(G):
            del weights[v]

    # Store the original graph, since G will be modified.
    G_original, G = G, G.copy(with_data=False)
    # Create a separate dictionary of weights, since the weights of each
    # node will be updated in the main loop.
    weights = Counter({u: G.node[u].get(weight, 1) for u in G})
    # Initially, F is the empty set. As the algorithm progresses, nodes
    # will be removed from the graph and added to F. At the end of the
    # algorithm, F will contain a feedback vertex set.
    F = set()
    # The stack stores the order in which nodes are removed from the graph.
    stack = []
    # First, remove all nodes of weight zero from the graph and add them
    # to F. Clean up the graph by removing any dangling tails.
    move_and_cleanup(G, F, weights)
    while G:
        # Try to find a semidisjoint cycle in the graph.
        try:
            C = next(semidisjoint_cycles(G))
        # If there are no semidisjoint cycles, update the degree-scaled
        # weights of all nodes.
        except StopIteration:
            gamma = min(weights[v] / (d - 1) for v, d in G.degree())
            weights -= Counter({v: gamma * (d - 1) for v, d in G.degree()})
        # Otherwise, only update the weights of the nodes in the cycle.
        else:
            gamma = min(weights[v] for v in C)
            weights -= Counter({v: gamma for v in C})
        # Remove all nodes of weight zero from the graph and add them to
        # F. Clean up the graph by removing any dangling tails.
        move_and_cleanup(G, F, weights, stack=stack)
    # Remove extraneous nodes from the feedback vertex set. A node v is
    # extraneous to the feedback vertex set F if F - {v} remains a
    # feedback vertex set in the original graph. This not only ensures a
    # minimal feedback vertex set but is also required to achieve the
    # approximation guarantee.
    while stack:
        v = stack.pop()
        if nx.is_forest(G_original.subgraph(set(G) - (F - {v}))):
            F.remove(v)
    return F
