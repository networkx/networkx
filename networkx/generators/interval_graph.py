"""
Generators for interval graph.
"""
from collections.abc import Sequence
import networkx as nx

__all__ = ['interval_graph']


def interval_graph(intervals):
    """ Generates an interval graph for a list of intervals given.

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

    Raises
    --------
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
            raise TypeError("Each interval must have length 2, and be a "
                            "collections.abc.Sequence such as tuple or list.")
        if interval[0] > interval[1]:
            raise ValueError(f"Interval must have lower value first. "
                             f"Got {interval}")

    graph = nx.Graph()
    if len(intervals) == 0:
        return graph

    tupled_intervals = [tuple(interval) for interval in intervals]
    graph.add_nodes_from(tupled_intervals)

    edges = []
    for i in range(len(intervals)):
        min1, max1 = tupled_intervals[i]
        for j in range(i + 1, len(intervals)):
            min2, max2 = tupled_intervals[j]
            if max1 >= min2 or max2 >= min1:
                edges.append((tupled_intervals[i], tupled_intervals[j]))

    graph.add_edges_from(edges)
    return graph
