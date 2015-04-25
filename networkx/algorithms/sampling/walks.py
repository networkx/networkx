# walks.py - random walks in a graph
#
# Copyright 2011 Maciej Kurant.
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for generating random walks in a graph."""
from __future__ import division

import itertools
import random

import networkx as nx
from networkx.exception import NetworkXError


def _random_walk(G, start_node, length, stay_probability):
    """Generates nodes sampled by a (possibly lazy) random walk.

    Parameters
    ----------
    G : NetworkX graph
        The graph from which to sample nodes.

    start_node : node
        The node from which the random walk starts. If not specified,
        then the starting node will be chosen uniformly at random.

    length : int
        The length of the random walk. If -1, the default, then the
        generator never stops yielding nodes. If zero, this function
        generates a single node.

    stay_probability : float
        A number between zero and one, inclusive, representing the
        probability that the walk remains on a node without actually
        taking a step to the next node. If this number is zero, the
        output sequence of nodes is guaranteed to never have two
        adjacent elements that are the same. If this number is one, the
        output sequence will remain on the start node forever.

    Returns
    -------
    iterator
       An iterator over nodes of the graph.

    """
    if start_node is None:
        start_node = random.choice(list(G))
    elif start_node not in G:
        msg = 'Node {0} not in the graph'.format(start_node)
        # TODO This exception should be changed to NodeNotFound.
        raise NetworkXError(msg)
    if not callable(stay_probability):
        probability = lambda v, c: stay_probability
    else:
        probability = stay_probability
    v = start_node
    yield v
    for c in itertools.count():
        if c == length:
            return
        candidate = random.choice([w for u, w in G.edges(v)])
        # Decide whether to take a step to the next node or remain on
        # the current node.
        if random.random() < 1 - probability(v, candidate):
            v = candidate
        yield v


def random_walk(G, start_node=None, length=-1):
    """Generates nodes sampled by a random walk.

    Parameters
    ----------
    G : a NetworkX graph
        The graph from which to sample nodes.

    start_node : node
        The node from which the random walk starts. If not specified,
        then the starting node will be chosen uniformly at random.

    length : int
        The length of the random walk. If -1, the default, then the
        generator never stops yielding nodes. If zero, this function
        generates a single node.

    Returns
    -------
    iterator
        An iterator over nodes of the graph.

    Examples
    --------
    A random walk of length ten::

        >>> G = nx.wheel_graph(10)
        >>> list(nx.sampling.random_walk(G, length=10))  # doctest: +SKIP
        [6, 7, 6, 7, 0, 3, 2, 3, 2, 0, 5]

    See also
    --------
    lazy_random_walk
    metropolis_hastings_random_walk

    """
    return _random_walk(G, start_node, length, 0)


def lazy_random_walk(G, start_node=None, length=-1):
    """Generates nodes sampled acording to a lazy random walk.

    Parameters
    ----------
    G : a NetworkX graph
       The graph from which to sample nodes.

    start_node : node
       The node from which the random walk starts. If not specified, then the
       starting node will be chosen uniformly at random.

    length : int
       The length of the random walk, that is, the number of nodes to sample
       from the graph. If -1, the default, then the generator never stops.

    Returns
    -------
    iterator
       An iterator over nodes of the graph.

    Notes
    -----
    In a lazy random walk on a graph without self-loops, there is a 50%
    chance of remaining on the current node instead of taking a step. If
    the graph already has self-loops, the chance of remaining on the
    current node will be greater.

    See also
    --------
    metropolis_hastings_random_walk
    random_walk

    """
    return _random_walk(G, start_node, length, 0.5)


def metropolis_hastings_random_walk(G, start_node=None, length=-1):
    """Generates nodes sampled according to a Metropolis--Hastings random
    walk, with the uniform target node distribution.

    Parameters
    ----------
    G : a NetworkX graph
        The graph from which to sample nodes.

    start_node : node
        The node from which the random walk starts. If not specified,
        then the starting node will be chosen uniformly at random.

    length : int
        The length of the random walk. If -1, the default, then the
        generator never stops yielding nodes. If zero, this function
        generates a single node.

    Returns
    -------
    iterator
        An iterator over nodes of the graph.

    See also
    --------
    lazy_random_walk
    random_walk

    """

    def stay_probability(node, next_node):
        """Returns the probability of remaining in the current node.

        ``node`` is the current node, ``next_node`` is the candidate for
        the next node in the walk.

        In the Metropolis--Hastings algorithm, the probability of taking
        a step to the next node is `d(v) / d(c)`, where `d(v)` is the
        degree of the current node and `d(c)` is the degree of the next
        node. This function returns `1 - d(v) / d(c)`, since it returns
        the probability of remaining on the current node.

        """
        return 1 - G.degree(node) / G.degree(next_node)

    return _random_walk(G, start_node, length, stay_probability)
