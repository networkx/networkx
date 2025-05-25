"""
Generators for interval graph.
"""

from collections.abc import Sequence
from heapq import heappop, heappush
from random import sample

import networkx as nx

__all__ = ["interval_graph"]


@nx._dispatchable(graphs=None, returns_graph=True)
def interval_graph(intervals, method="dense"):
    """Generates an interval graph for a list of intervals given.

    In graph theory, an interval graph is an undirected graph formed from a set
    of closed intervals on the real line, with a vertex for each interval
    and an edge between vertices whose intervals intersect.
    It is the intersection graph of the intervals.

    More information can be found at:
    https://en.wikipedia.org/wiki/Interval_graph

    Parameters
    ----------
    intervals : a sequence of intervals, say (l, r) where l is the left end,
    and r is the right end of the closed interval.

    Returns
    -------
    G : networkx graph

    Examples
    --------
    >>> intervals = [(-2, 3), [1, 4], (2, 3), (4, 6)]
    >>> G = nx.interval_graph(intervals)
    >>> sorted(G.edges)
    [((-2, 3), (1, 4)), ((-2, 3), (2, 3)), ((1, 4), (2, 3)), ((1, 4), (4, 6))]

    Raises
    ------
    :exc:`TypeError`
        if `intervals` contains None or an element which is not
        collections.abc.Sequence or not a length of 2.
    :exc:`ValueError`
        if `intervals` contains an interval such that min1 > max1
        where min1,max1 = interval
    """
    intervals = list(intervals)
    for interval in intervals:
        if not (isinstance(interval, Sequence) and len(interval) == 2):
            raise TypeError(
                "Each interval must have length 2, and be a "
                "collections.abc.Sequence such as tuple or list."
            )
        if interval[0] > interval[1]:
            raise ValueError(f"Interval must have lower value first. Got {interval}")

    if method == "dense":
        return _interval_graph_dense(intervals)
    elif method == "sparse":
        return _interval_graph_sparse(intervals)
    elif method == "auto":
        return _interval_graph_auto(intervals)
    else:
        raise ValueError(f"Method not supported: {method}")


def _interval_graph_auto(intervals):
    sampled_intervals = sample(intervals, len(intervals) // 20)
    graph = _interval_graph_dense(sampled_intervals)
    if len(graph.edges) > len(sampled_intervals) ** 2 // 4:
        return _interval_graph_dense(intervals)
    else:
        return _interval_graph_sparse(intervals)


def _interval_graph_dense(intervals):
    graph = nx.Graph()
    tupled_intervals = [tuple(interval) for interval in intervals]
    graph.add_nodes_from(tupled_intervals)

    while tupled_intervals:
        min1, max1 = interval1 = tupled_intervals.pop()
        for interval2 in tupled_intervals:
            min2, max2 = interval2
            if max1 >= min2 and max2 >= min1:
                graph.add_edge(interval1, interval2)
    return graph


def _interval_graph_sparse(intervals):
    """A "sweep line"-like algorithm to find intersections of intervals."""
    graph = nx.Graph()

    # Sort by starting point.
    tupled_intervals = sorted(tuple(interval) for interval in intervals)
    graph.add_nodes_from(tupled_intervals)

    # Keeps all intervals that intersect with the current interval,
    # sorted by ending point.
    heap = []

    for i1, interval1 in enumerate(tupled_intervals):
        start1, end1 = interval1

        # Remove intervals that don't intersect anymore.
        while heap and heap[0][0] < start1:
            heappop(heap)

        graph.add_edges_from((interval1, tupled_intervals[i2]) for _, i2 in heap)

        # Add the current interval to intersection list.
        heappush(heap, (end1, i1))

    return graph
