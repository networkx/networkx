#    Copyright(C) 2011-2019 by
#    Jangwon Yie <kleinaberoho10@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:  Jangwon Yie (kleinaberoho10@gmail.com)

"""
Generators for interval graph.

"""

import networkx as nx

__all__ = ['interval_graph']


def interval_graph(intervals):
    """ Generates an interval graph for a list of intervals given.

    In graph theory, an interval graph is an undirected graph formed from a set of intervals
    on the real line, with a vertex for each interval and an edge between vertices whose
    intervals intersect. It is the intersection graph of the intervals.

    More information can be found at:
    https://en.wikipedia.org/wiki/Interval_graph

    Parameters
    ----------
    intervals : a list of intervals, each element of which is a form of tuple,
    say (l, r) where l,r is a left end, right end of an closed interval, respectively.
    Followings are invalid intervals.

    # an element is not a tuple
    # a tuple element, but its length is not 2.

    Invalid intervals will be ignored.

    Returns
    -------
    G : networkx graph
    """

    if intervals is None or len(intervals) == 0:
        return None

    graph = nx.Graph()
    valid_intervals = {interval for interval in intervals if __check_interval(interval)}

    graph.add_nodes_from(valid_intervals)
    sorted_ = sorted(valid_intervals, key=lambda x:x[0])

    edges = list()
    for i in range(len(valid_intervals)):
        node = sorted_[i]
        for j in range(i + 1, len(valid_intervals)):
            if sorted_[j][0] <= node[1]:
                edges.append((node, sorted_[j]))
            else:
                break

    graph.add_edges_from(edges)

    return graph


def __check_interval(interval):

    return interval is not None and isinstance(interval, tuple) and len(interval) == 2
