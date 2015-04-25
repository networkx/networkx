# edges.py - sampling edges from a graph
#
# Copyright 2011 Maciej Kurant.
# Copyright 2016 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for sampling edges from a graph."""
import random

from .helpers import sample_with_replacement

__all__ = ['uniform_independent_edge_sample']


def uniform_independent_edge_sample(G, size=-1, with_replacement=False,
                                    keys=False, data=False):
    """Returns a list of edges sampled uniformly at random from the
    graph ``G`` without replacement.

    Parameters
    ----------
    G : NetworkX graph
        The graph from which to sample the edges.

    size: int
        The number of nodes to sample from the graph. If size is -1, the
        default, then the generator never stops.

    with_replacement : bool
        Whether to sample with replacement or not.

    keys : bool
        Whether to return edge keys in addition to the endpoints of the
        edge. This argument is only used if ``G`` is a multigraph.

    data : bool
        Whether to return edge data in addition to the endpoints of the
        edge.

    Raises
    ------
    ValueError
        If ``size`` is ``-1`` and ``with_replacement`` is ``False``,
        since sampling without replacement can only be done if the
        sample size is finite and at most the size of the population.

    Returns
    -------
    list or iterator
        An iterator over edges of the graph sampled with replacement if
        ``with_replacement`` is ``True``, otherwise a list of edges
        sampled without replacement.

        If ``data`` is ``True``, each element of the list will be a
        three-tuple of the form ``(u, v, data)``, where ``u`` and ``v``
        are the endpoints of the edge and ``data`` is the edge data. If
        ``data`` is ``False``, each element of the list will be a
        two-tuple of the form ``(u, v)``. If ``keys`` is ``True`` and
        ``G`` is a multigraph, the tuples will be of the form ``(u, v,
        k)`` or ``(u, v, k, d)``.

    """
    if G.is_multigraph():
        edges = G.edges(keys=keys, data=data)
    else:
        edges = G.edges(data=data)
    if with_replacement:
        return sample_with_replacement(list(edges), size=size)
    if size == -1:
        msg = 'sampling without replacement must have a sample size'
        raise ValueError(msg)
    return random.sample(list(edges), size)
