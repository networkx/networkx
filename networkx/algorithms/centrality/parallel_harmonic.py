#    Copyright (C) 2019 by
#    Luca Cappelletti
#    MIT license.
#
# Authors:
#    Luca Cappelletti <cappelletti.luca@studenti.unimi.it>
#
"""Functions for computing the harmonic centrality of a graph using multiprocessing and caching."""
from multiprocessing import Pool, cpu_count
from math import ceil
from collections import ChainMap
from .harmonic import harmonic_centrality

__all__ = ['parallel_harmonic_centrality']


def _harmonic_centrality(task):
    return harmonic_centrality(*task)


def _tasks(G, nbunch, distance, n):
    """Yield successive n equally sized nbunch from graphs with task arguments."""
    return (
        (G, nbunch[i:i + n], distance)
        for i in range(0, len(nbunch), n)
    )


def parallel_harmonic_centrality(G, nbunch=None, distance=None, n=None):
    r"""Compute harmonic centrality for nodes in parallel fashion.
    Parameters
    ----------
    G : graph
      A NetworkX graph

    nbunch : container
      Container of nodes. If provided harmonic centrality will be computed
      only over the nodes in nbunch.

    distance : edge attribute key, optional (default=None)
      Use the specified edge attribute as the edge distance in shortest
      path calculations.  If `None`, then each edge will have distance equal to 1.

    n: integer,
      Size of the chunks of nodes to parse by a single job.

    Returns
    -------
    nodes : dictionary
      Dictionary of nodes with harmonic centrality as the value.
    """
    if nbunch is None:
        nbunch = list(G.nodes)
    if len(nbunch) == 0:
        return {}
    if n is None:
        n = ceil(len(nbunch) / cpu_count())
    with Pool(min(cpu_count(), n)) as p:
        results = dict(ChainMap(*list(
            p.imap(_harmonic_centrality, _tasks(G, nbunch, distance, n))
        )))
        p.close()
        p.join()
    return results
