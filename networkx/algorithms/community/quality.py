# quality.py - functions for measuring partitions of a graph
#
# Copyright 2015 NetworkX developers.
#
# This file is part of NetworkX.
#
# NetworkX is distributed under a BSD license; see LICENSE.txt for more
# information.
"""Functions for measuring the quality of a partition (into
communities).

"""
from __future__ import division

from functools import wraps

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['coverage', 'performance']


def is_partition(G, partition):
    """Returns True if and only if `partition` is a partition of
    the nodes of `G`.

    A partition of a universe set is a family of pairwise disjoint sets
    whose union equals the universe set.

    `G` is a NetworkX graph.

    `partition` is a sequence (not an iterator) of sets of nodes of
    `G`.

    """
    # Alternate implementation:
    #
    #     return (len(G) == sum(len(c) for c in community) and
    #             set(G) == set().union(*community))
    #
    return all(sum(1 if v in c else 0 for c in partition) == 1 for v in G)


def require_partition(func):
    """Decorator that raises an exception if a partition is not a valid
    partition of the nodes of a graph.

    Raises :exc:`networkx.NetworkXError` if the partition is not valid.

    This decorator should be used on functions whose first two arguments
    are a graph and a partition of the nodes of that graph (in that
    order)::

        >>> @require_partition
        ... def foo(G, partition):
        ...     print('partition is valid!')
        ...
        >>> G = nx.complete_graph(5)
        >>> partition = [{0, 1}, {2, 3}, {4}]
        >>> foo(G, partition)
        partition is valid!
        >>> partition = [{0}, {2, 3}, {4}]
        >>> foo(G, partition)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          ...
        NetworkXError: `partition` is not a valid partition of the nodes of G
        >>> partition = [{0, 1}, {1, 2, 3}, {4}]
        >>> foo(G, partition)  # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          ...
        NetworkXError: `partition` is not a valid partition of the nodes of G

    """

    @wraps(func)
    def new_func(*args, **kw):
        # Here we assume that the first two arguments are (G, partition).
        if not is_partition(*args[:2]):
            raise nx.NetworkXError('`partition` is not a valid partition of'
                                   ' the nodes of G')
        return func(*args, **kw)
    return new_func


def intra_community_edges(G, partition):
    """Returns the number of intra-community edges according to the given
    partition of the nodes of `G`.

    `G` must be a NetworkX graph.

    `partition` must be a partition of the nodes of `G`.

    The "intra-community edges" are those edges joining a pair of nodes
    in the same block of the partition.

    """
    return sum(G.subgraph(block).size() for block in partition)


def inter_community_edges(G, partition):
    """Returns the number of inter-community edges according to the given
    partition of the nodes of `G`.

    `G` must be a NetworkX graph.

    `partition` must be a partition of the nodes of `G`.

    The *inter-community edges* are those edges joining a pair of nodes
    in different blocks of the partition.

    Implementation note: this function creates an intermediate graph
    that may require the same amount of memory as required to store
    `G`.

    """
    # Alternate implementation that does not require constructing a new
    # graph object (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in G.edges() if aff[u] != aff[v])
    #
    return nx.quotient_graph(G, partition, create_using=nx.MultiGraph()).size()


def inter_community_non_edges(G, partition):
    """Returns the number of inter-community non-edges according to the
    given partition of the nodes of `G`.

    `G` must be a NetworkX graph.

    `partition` must be a partition of the nodes of `G`.

    A *non-edge* is a pair of nodes (undirected if `G` is undirected)
    that are not adjacent in `G`. The *inter-community non-edges* are
    those non-edges on a pair of nodes in different blocks of the
    partition.

    Implementation note: this function creates two intermediate graphs,
    which may require up to twice the amount of memory as required to
    store `G`.

    """
    # Alternate implementation that does not require constructing two
    # new graph objects (but does require constructing an affiliation
    # dictionary):
    #
    #     aff = dict(chain.from_iterable(((v, block) for v in block)
    #                                    for block in partition))
    #     return sum(1 for u, v in nx.non_edges(G) if aff[u] != aff[v])
    #
    return inter_community_edges(nx.complement(G), partition)


@not_implemented_for('multigraph')
@require_partition
def performance(G, partition):
    """Returns the performance of a partition.

    The *performance* of a partition is the ratio of the number of
    intra-community edges plus inter-community non-edges with the total
    number of potential edges.

    Parameters
    ----------
    G : NetworkX graph
        A simple graph (directed or undirected).

    partition : sequence

        Partition of the nodes of `G`, represented as a sequence of
        sets of nodes. Each block of the partition represents a
        community.

    Returns
    -------
    float
        The performance of the partition, as defined above.

    Raises
    ------
    NetworkXError
        If `partition` is not a valid partition of the nodes of `G`.

    References
    ----------
    .. [1] Santo Fortunato.
           "Community Detection in Graphs".
           *Physical Reports*, Volume 486, Issue 3--5 pp. 75--174
           <http://arxiv.org/abs/0906.0612>

    """
    # Compute the number of intra-community edges and inter-community
    # edges.
    intra_edges = intra_community_edges(G, partition)
    inter_edges = inter_community_non_edges(G, partition)
    # Compute the number of edges in the complete graph (directed or
    # undirected, as it depends on `G`) on `n` nodes.
    #
    # (If `G` is an undirected graph, we divide by two since we have
    # double-counted each potential edge. We use integer division since
    # `total_pairs` is guaranteed to be even.)
    n = len(G)
    total_pairs = n * (n - 1)
    if not G.is_directed():
        total_pairs //= 2
    return (intra_edges + inter_edges) / total_pairs


@require_partition
def coverage(G, partition):
    """Returns the coverage of a partition.

    The *coverage* of a partition is the ratio of the number of
    intra-community edges to the total number of edges in the graph.

    Parameters
    ----------
    G : NetworkX graph

    partition : sequence
        Partition of the nodes of `G`, represented as a sequence of
        sets of nodes. Each block of the partition represents a
        community.

    Returns
    -------
    float
        The coverage of the partition, as defined above.

    Raises
    ------
    NetworkXError
        If `partition` is not a valid partition of the nodes of `G`.

    Notes
    -----
    If `G` is a multigraph, the multiplicity of edges is counted.

    References
    ----------
    .. [1] Santo Fortunato.
           "Community Detection in Graphs".
           *Physical Reports*, Volume 486, Issue 3--5 pp. 75--174
           <http://arxiv.org/abs/0906.0612>

    """
    intra_edges = intra_community_edges(G, partition)
    total_edges = G.number_of_edges()
    return intra_edges / total_edges
