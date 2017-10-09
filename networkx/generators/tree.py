# -*- encoding: utf-8 -*-
# tree.py - functions for generating trees
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for generating trees."""
import random

import networkx as nx

__all__ = ['random_tree']


def sample_with_replacement(population, k):
    """Returns a sample of size ``k`` from the given population.

    ``population`` must be a sequence and ``k`` must be a positive
    integer.

    This function returns a list of ``k`` elements chosen uniformly at
    random from ``population``.

    """
    return [random.choice(population) for i in range(k)]


# From the Wikipedia article on Prüfer sequences:
#
# > Generating uniformly distributed random Prüfer sequences and
# > converting them into the corresponding trees is a straightforward
# > method of generating uniformly distributed random labelled trees.
#
def random_tree(n, seed=None):
    """Returns a uniformly random tree on `n` nodes.

    Parameters
    ----------
    n : int
        A positive integer representing the number of nodes in the tree.

    seed : int
        A seed for the random number generator.

    Returns
    -------
    NetworkX graph
        A tree, given as an undirected graph, whose nodes are numbers in
        the set {0, …, *n* - 1}.

    Raises
    ------
    NetworkXPointlessConcept
        If `n` is zero (because the null graph is not a tree).

    Notes
    -----
    The current implementation of this function generates a uniformly
    random Prüfer sequence then converts that to a tree via the
    :func:`~networkx.from_prufer_sequence` function. Since there is a
    bijection between Prüfer sequences of length *n* - 2 and trees on
    *n* nodes, the tree is chosen uniformly at random from the set of
    all trees on *n* nodes.

    """
    if n == 0:
        raise nx.NetworkXPointlessConcept('the null graph is not a tree')
    # Cannot create a Prüfer sequence unless `n` is at least two.
    if n == 1:
        return nx.empty_graph(1)
    random.seed(seed)
    sequence = sample_with_replacement(range(n), n - 2)
    return nx.from_prufer_sequence(sequence)
