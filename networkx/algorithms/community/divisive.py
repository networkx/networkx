import functools
import random
from operator import itemgetter

import networkx as nx

__all__ = [
    "edge_betweenness_partition",
    "edge_current_flow_betweenness_partition",
]


def _divisive_partition(G, number_of_sets, edge_ranking):
    """Partition created by iteratively removing the highest `edge_ranking` edge.

    Parameters
    ----------
    G : NetworkX Graph
      The graph to be partitioned

    number_of_sets : int
      Number of sets in the desired partition.

    edge_ranking : function from NetworkXGraph to dict
      A function that takes a NetworkXGraph as a single
      parameter and returns a dictionary keyed by
      edges. The values in the dictionary must be
      comparable.

    Returns
    -------
    partition : list of sets
      Partition of the nodes of G

    Raises
    ------
    NetworkXError
      If number_of_sets is <= 0 or if number_of_sets > len(G)
    """
    if number_of_sets <= 0:
        raise nx.NetworkXError("number_of_sets must be >0")
    elif number_of_sets == 1:
        return [set(G)]
    elif number_of_sets == len(G):
        return [{n} for n in G]
    elif number_of_sets > len(G):
        raise nx.NetworkXError("number_of_sets must be <= len(G)")

    H = G.copy()
    while True:
        cc = list(nx.connected_components(H))
        if len(cc) >= number_of_sets:
            break
        ranking = edge_ranking(H).items()
        edge = max(ranking, key=itemgetter(1))[0]
        H.remove_edge(*edge)
    return cc


def edge_betweenness_partition(G, number_of_sets, normalized=True, weight=None):
    """Partition created by iteratively removing the highest edge betweenness edge.

    This algorithm works by calculating the edge betweenness for all
    edges and removing the edge with the highest value. It is then
    determined whether the graph has been broken into at least
    `number_of_sets` connected components.
    If not the process is repeated.

    Parameters
    ----------
    G : NetworkX Graph, DiGraph or MultiGraph
      Graph to be partitioned

    number_of_sets : int
      Number of sets in the desired partition of the graph

    normalized : boolean optional, default=True
      Whether to normalize the edge betweenness calculation

    weight : key, optional, default=None
      The key to use if using weights for edge betweenness calculation

    Returns
    -------
    C : list of sets
      Partition of the nodes of G

    Raises
    ------
    NetworkXError
      If number_of_sets is <= 0 or if number_of_sets > len(G)

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> part = nx.community.edge_betweenness_partition(G, 2)
    >>> {0, 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21} in part
    True
    >>> {2, 8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33} in part
    True

    See Also
    --------
    edge_current_flow_betweenness_partition

    Notes
    -----
    This algorithm is fairly slow, as both the calculation of connected
    components and edge betweenness relies on all pairs shortest
    path algorithms. They could potentially be combined to cut down
    on overall computation time.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174
       http://arxiv.org/abs/0906.0612
    """
    ranking = functools.partial(
        nx.edge_betweenness_centrality, normalized=normalized, weight=weight
    )
    return _divisive_partition(G, number_of_sets, ranking)


def edge_current_flow_betweenness_partition(
    G, number_of_sets, normalized=True, weight=None
):
    """Partition created by removing the highest edge current flow betweenness edge.

    This algorithm works by calculating the edge current flow
    betweenness for all edges and removing the edge with the
    highest value. It is then determined whether the graph has
    been broken into at least `number_of_sets` connected
    components. If not the process is repeated.

    Parameters
    ----------
    G : NetworkX Graph, DiGraph or MultiGraph
      Graph to be partitioned

    number_of_sets : int
      Number of sets in the desired partition of the graph

    normalized : boolean optional, default=True
      Whether to normalize the edge betweenness calculation

    weight : key, optional, default=None
      The key to use if using weights for edge betweenness calculation

    Returns
    -------
    C : list of sets
      Partition of G

    Raises
    ------
    NetworkXError
      If number_of_sets is <= 0 or number_of_sets > len(G)

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> part = nx.community.edge_current_flow_betweenness_partition(G, 2)
    >>> {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 16, 17, 19, 21} in part
    True
    >>> {8, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33} in part
    True


    See Also
    --------
    edge_betweenness_partition

    Notes
    -----
    This algorithm is extremely slow, as the recalculation of the edge
    current flow betweenness is extremely slow.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174
       http://arxiv.org/abs/0906.0612
    """
    ranking = functools.partial(
        nx.edge_current_flow_betweenness_centrality,
        normalized=normalized,
        weight=weight,
    )
    return _divisive_partition(G, number_of_sets, ranking)
