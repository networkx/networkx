#    Copyright(C) 2011-2019 by
#    Jangwon Yie <kleinaberoho10@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:  Jangwon Yie (kleinaberoho10@gmail.com)

"""
Generators for interval graph.
"""
from collections.abc import Sequence
import networkx as nx

__all__ = ['interval_graph']


def interval_graph(intervals):
    """ Generates an interval graph for a list of intervals given.

    In graph theory, an interval graph is an undirected graph formed from a set
    of intervals on the real line, with a vertex for each interval and an edge
    between vertices whose intervals intersect.
    It is the intersection graph of the intervals.

    More information can be found at:
    https://en.wikipedia.org/wiki/Interval_graph

    Parameters
    ----------
    intervals : a list of intervals, each element of which is a form of
    collection.abc.Sequence, say (l, r) where l,r is a left end, right
    end of an closed interval, respectively.

    Returns
    -------
    G : networkx graph

    Raises
    ------
    :exc:`TypeError`
        If `intervals` contains None or an element which is not
        collections.abc.Sequence or not a length of 2.
    :exc:`ValueError`
        If `intervals` contains an interval such that min1 > max1
        where min1,max1 = interval

    Examples
    --------
    Following is an example to generate interval_graph which is actually K_3.
    >>> import networkx as nx
    >>> intervals = [(1, 4), [3, 5], [2.5, 4]]
    >>> G = nx.interval_graph(intervals)
    >>> len(G.nodes)
    3
    >>> len(G.edges)
    3

    Another example which is an independent graph of order 4 follows.
    >>> intervals = [(1, 2), [3, 5], [6, 8], (9, 10)]
    >>> G = nx.interval_graph(intervals)
    >>> len(G.nodes)
    4
    >>> len(G.edges)
    0
    """

    if intervals is None or len(intervals) == 0:
        return None

    for interval in intervals:
        if not __check_interval_type(interval):
            raise TypeError('Each interval must be not None, an instance of '
                            'collections.abc.Sequence and a 2-tuple.')
        if not __check_interval_val(interval):
            raise ValueError("Each interval must be a 2-tuple (min, max). "
                             "Got {}".format(interval))

    graph = nx.Graph()
    tupled_intervals = [tuple(interval) for interval in intervals]
    graph.add_nodes_from(tupled_intervals)

    edges = list()
    intervals = list(intervals)
    for i in range(len(intervals)):
        min1, max1 = tupled_intervals[i]
        for j in range(i + 1, len(intervals)):
            min2, max2 = tupled_intervals[j]
            if max1 >= min2 or max2 >= min1:
                edges.append((tupled_intervals[i], tupled_intervals[j]))

    graph.add_edges_from(edges)

    return graph


def __check_interval_type(interval):
    return interval is not None and isinstance(interval, Sequence)\
           and len(interval) == 2


def __check_interval_val(interval):
    min1, max1 = interval
    return min1 <= max1
