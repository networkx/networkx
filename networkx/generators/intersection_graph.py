#    Copyright(C) 2011-2019 by
#    Jangwon Yie <kleinaberoho10@gmail.com>
#    All rights reserved.
#    BSD license.
#
# Authors:  Jangwon Yie (kleinaberoho10@gmail.com)

"""
Generators for intersection graph(https://en.wikipedia.org/wiki/Intersection_graph).
"""

import networkx as nx
from collections.abc import Collection

__all__ = ['intersection_graph']


def intersection_graph(sets):
    """ Generates an intersection graph for a list of sets given.
    In the mathematical area of graph theory, an intersection graph is a graph
    that represents the pattern of intersections of a family of sets.
    Any graph can be represented as an intersection graph, but some important
    special classes of graphs can be defined by the types of sets that are used
    to form an intersection representation of them.
    More information can be found at:

    https://en.wikipedia.org/wiki/Intersection_graph

    Parameters
    ----------
    sets : a list of sets, each element of which is a form of
    set, dict, list and a single element.
    If sets is None or length of sets is 0 then it returns None.

    Returns
    -------
    G : networkx graph

    Raises
    --------
    :exc:`TypeError`
        if 'sets' is not a collection type
        if 'sets' is string
        if `sets` contains None, empty collection, dict element.

    """

    if sets is None:
        return None

    if not isinstance(sets, Collection) or isinstance(sets, dict) or \
            isinstance(sets, str):
        raise TypeError("sets must be a none dict type collection.")

    if len(sets) == 0:
        return None

    graph = nx.Graph()
    ordered_tuples = list({__check_type_and_convert(_set) for _set in sets})

    graph.add_nodes_from(ordered_tuples)
    edges = list()
    for i in range(len(ordered_tuples)):
        node = ordered_tuples[i]
        for j in range(i + 1, len(ordered_tuples)):
            c_node = ordered_tuples[j]
            if len(set(node).intersection(set(c_node))) > 0:
                edges.append((node, c_node))

    graph.add_edges_from(edges)

    return graph


def __check_type_and_convert(_set):
    if _set is None:
        raise TypeError("None element is not allowed.")

    if isinstance(_set, dict):
        raise TypeError("dict type is not allowed.")

    if isinstance(_set, Collection):
        if len(_set) == 0:
            raise TypeError("a collection having zero length is not allowed.")
        else:
            return tuple(sorted(_set))

    return tuple({_set})
