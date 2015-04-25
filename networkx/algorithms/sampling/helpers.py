# helpers.py - helper functions for sampling
#
# Copyright 2011 Maciej Kurant.
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Generic functions for sampling from a population, with and without
replacement.

"""
import bisect
import itertools
import random

from networkx.utils import accumulate


def weighted_sample_with_replacement(population, weights, size=-1):
    """Generates random items with replacement from a population,
    sampled according to a weight.

    This function is an iterator generator.

    Parameters
    ----------
    population : list
        List of elements from which to sample.

    weights : function
        A single-input function that returns a non-negative number. The
        input is an element of population and the output represents how
        likely it is to be chosen, the higher the number, the more
        likely it is to be chosen.

    size : int
        Desired number of samples. If this is ``-1``, the default, then the
        generator never stops.

    Returns
    -------
    iterator
        An iterator over elements of ``population``.

    """
    cum_weights = list(accumulate(weights(v) for v in population))
    tot_weight = cum_weights[-1]
    for c in itertools.count():
        if c == size:
            return
        i = bisect.bisect_right(cum_weights, random.random() * tot_weight)
        yield population[i]


def sample_with_replacement(population, size=-1):
    """Generates random items with replacement from a population.

    This function is an iterator generator.

    Parameters
    ----------
    population : list
       List of elements from which to sample.

    size : int
       Desired number of samples. If this is ``-1``, the default, then the
       generator never stops.

    Returns
    -------
    iterator
        An iterator over elements of ``population``.

    """
    # This could be implemented as
    #
    #     return weighted_sample_with_replacement(G, lambda x: 1, size=size)
    #
    # but the below should be a little faster since it is simpler.
    for c in itertools.count():
        if c == size:
            return
        yield random.choice(population)
