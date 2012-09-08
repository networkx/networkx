import functools
from operator import itemgetter
import random
import networkx as nx
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])

def divisive_partition(G, number_of_partitions, edge_ranking):
    # edge ranking is a function that returns a dictionary
    """Return the partition created by successively removing
    the edge with the highest value as measured by edge_ranking.

    Parameters
    ----------
    G : NetworkX Graph
    number_of_partitions : int
      Number of partitions to create
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
      If the number of partitions is not in (0,len(G)]

    See Also
    --------
    edge_betweenness_partition
    edge_current_betweenness_partition
    """
    if number_of_partitions <= 0:
        raise nx.NetworkXError("number_of_partitions must be >0")
    elif number_of_partitions == 1:
        return [set(G)]
    elif number_of_partitions == len(G):
        return map(set,[[n] for n in G])
    elif number_of_partitions > len(G):
        raise nx.NetworkXError("number_of_partitions must be <= len(G)")

    H = G.copy()
    while True:
        cc = nx.connected_components(H)
        if len(cc) >= number_of_partitions:
            break
        ranking = edge_ranking(H).items()
        edge = max(ranking,key=itemgetter(1))[0]
        H.remove_edge(*edge)
    return map(set,cc)

def edge_betweenness_partition(G, number_of_partitions, normalized=True,
                               weight=None):
    """Return the partition created by successively removing
    the edge with the highest edge betweenness.

    This algorithm works by calculating the edge betweenness for all
    edges and removing the edge with the highest value. It is then
    determined whether the graph has been broken into connected
    components equal to the number of partitions. If so the partition
    is returned

    Parameters
    ----------
    G : NetworkX Graph, DiGraph or MultiGraph
      Graph to be partitioned
    number_of_partitions : int
      Number of partitions of the graph
    normalized : boolean optional, default=True
      Whether to normalize the edge betweenness calculation
    weight : key, optional, default=None
      The key to use if using wieghts for edge betweenness calculation

    Returns
    -------
    C : list of sets
      Partition of G

    Raises
    ------
    NetworkXError
      If number_of_partitions is <= 0 or if
      number_of_partitions > len(G)
      
    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> nx.edge_betweenness_partition(G,2)
    [set([2,8,9,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33]),
     set([0,1,3,4,5,6,7,10,11,12,13,16,17,19,21])]

    See Also
    --------
    edge_current_flow_betweenness_partition
    divisive partition

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
       http://arxiv.org/abs/0906.0612"""
    ranking = functools.partial(nx.edge_betweenness_centrality,
                                normalized=normalized,
                                weight=weight)
    return divisive_partition(G, number_of_partitions, ranking)

def edge_current_flow_betweenness_partition(G, number_of_partitions, 
                                            normalized=True,  weight=None):
    """Return the partition created by successively removing
    the edge with the highest edge current flow betweenness.

    This algorithm works by calculating the edge current flow
    betweenness for all edges and removing the edge with the
    highest value. It is then determined whether the graph has
    been broken into connected components equal to the number
    of partitions. If so the partition is returned.

    Parameters
    ----------
    G : NetworkX Graph, DiGraph or MultiGraph
      Graph to be partitioned
    number_of_partitions : int
      Number of partitions of the graph
    normalized : boolean optional, default=True
      Whether to normalize the edge betweenness calculation
    weight : key, optional, default=None
      The key to use if using wieghts for edge betweenness calculation

    Returns
    -------
    C : list of sets
      Partition of G


    Raises
    ------
    NetworkXError
      If number_of_partitions is <= 0 or
      number_of_partitions > len(G)

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> nx.edge_current_flow_betweenness_partition(G,2)
    [set([0,1,2,3,4,5,6,7,9,10,11,12,13,16,17,19,21]),
     set([8,14,15,18,20,22,23,24,25,26,27,28,29,30,31,32,33])]


    See Also
    --------
    edge_betweenness_partition
    divisive_partition

    Notes
    -----
    This algorithm is extremely slow, as the recalculation of the edge
    current flow betweenness is extremely slow.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174
       http://arxiv.org/abs/0906.0612"""
    ranking = functools.partial(nx.edge_current_flow_betweenness_centrality,
                                normalized=normalized,
                                weight=weight)
    return divisive_partition(G, number_of_partitions, ranking)


if __name__=='__main__':
    G = nx.barbell_graph(3,0)
    C = edge_current_flow_betweenness_partition(G,2)
#    C = edge_betweenness_partition2(G,2)
    print C
#    assert_equal([set([0,1,2]),set([3,4,5])],C)

