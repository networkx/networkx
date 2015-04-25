# nodes.py - sampling nodes from a graph
#
# Copyright 2011 Maciej Kurant.
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for sampling nodes from a graph."""
import random

import networkx as nx
from .helpers import sample_with_replacement
from .helpers import weighted_sample_with_replacement

__all__ = ['degree_weighted_independent_node_sample',
           'uniform_independent_node_sample']


def uniform_independent_node_sample(G, size=-1, with_replacement=False):
    """Generates a uniform independent sample of nodes with replacement.

    Parameters
    ----------
    G : a NetworkX graph
        The graph whose nodes will be sampled.

    size: int
        The number of nodes to sample from the graph. If size is -1, the
        default, then the generator never stops.

    with_replacement : bool
        Whether to sample with replacement or not.

    Returns
    -------
    list or iterator
        An iterator over nodes of the graph if ``with_replacement`` is
        ``True``, otherwise a list of nodes.

    Examples
    --------
    Sampling twenty nodes uniformly at random from the wheel graph on ten
    vertices::

        >>> G = nx.generators.wheel_graph(10)
        >>> sample = nx.sampling.uniform_independent_node_sample
        >>> list(sample(G, size=10))  # doctest: +SKIP
        [8, 6, 4, 7, 9, 5, 5, 2, 4, 5]

    Raises
    ------
    ValueError
        If ``size`` is ``-1`` and ``with_replacement`` is ``False``,
        since sampling without replacement can only be done if the
        sample size is finite and at most the size of the population.

    """
    if with_replacement:
        return sample_with_replacement(list(G), size=size)
    if size == -1:
        msg = 'sampling without replacement must have a sample size'
        raise ValueError(msg)
    return random.sample(list(G), size)


def degree_weighted_independent_node_sample(G, size=-1):
    """Generates an independent sample of nodes with replacement, with
    sampling probabilities proportional to node degrees.

    Parameters
    ----------
    G : a NetworkX graph
        The graph whose nodes will be sampled.

    size: int
        The number of nodes to sample from the graph. If size is -1, the
        default, then the generator never stops.

    Returns
    -------
    iterator
        An iterator over nodes of the graph.

    """
    # # Faster:
    # for v in sample_with_replacement(G, size=size):
    #     yield random.choice(graph.neighbors(v))
    return weighted_sample_with_replacement(list(G), G.degree, size=size)
