import networkx as nx

#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])


def cut_size(G, c1, c2, weight='weight'):
    """Determine the cut size between two communities

    The cut size is the sum of the costs (weights) of the edges
    between two sets. For unweighted graphs the cost of an edge
    is 1.

    Parameters
    ----------
    G : NetworkX Graph
    c1,c2 : set
      community 1
    weight : key
      Edge data key to use as weight.  If None all edges have weight 1.

    Returns
    -------
    cut_size: int
      Number of edges between two communities

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> nx.cut_size(G,nx.spectral_partition(G),0,1)
    1
    >>> G = nx.Multigraph()
    >>> G.add_edge('a','b')
    >>> G.add_edge('a','b')
    >>> nx.cut_size(G,set(['a']),set(['b']))
    2

    Notes
    -----
    If Using MultiGraph or MultiDiGraph the cut is the total number
    of edges including multiplicity, or the sum of the weights on
    the multiple edges.

    References
    ----------
    """
    cut_size = sum(d.get(weight,1) for u,v,d
                   in G.edges_iter(c1,data=True) if v in c2)
    if G.is_directed():
        cut_size += sum(d.get(weight,1) for u,v,d
                        in G.edges_iter(c2,data=True) if v in c1)
    return cut_size

def volume(G,S,weight=None):
    """Returns the volume of a set of vertices on a graph G

    Volume is defined as the sum of weights on edges from vertices
    in S. [1]

    Parameters
    ----------
    G : NetworkX Graph
    S : container
      container of nodes
    weight : keyword, optional default=None
      keyword for weight on the edges.

    Returns
    -------
    volume : numeric
      volume of the container S in G

    See Also
    --------
    normalized_cut_size
    conductance
    expansion

    References
    ----------
    ..[1] David Gleich. 'Heirarchicical Directed Spectral Graph Partitioning'. Website
          report. http://www.stanford.edu/~dgleich/publications/directed-spectral.pdf

    """
    return sum(d.get(weight,1) for u,v,d in G.edges_iter(S,data=True))

def normalized_cut_size(G,c1,c2,weight=None):
    """Returns the normalized cut size between two containers of nodes
    c1 and c2.

    The normalized cut size is defined as the cut size times the sum
    of the reciprocal sizes of the volumes of the two cuts.[1]

    Parameters
    ----------
    G : NetworkX Graph
    c1, c2 : container
      containsers of nodes
    weight : keyword, optional default=None
      keyword for weight on edges

    Returns
    -------
    normalized_cut_size : float

    See Also
    --------
    cut_size
    volume
    conductance
    expansion

    References
    ----------
    ..[1] David Gleich. 'Heirarchicical Directed Spectral Graph Partitioning'. Website
          report. http://www.stanford.edu/~dgleich/publications/directed-spectral.pdf
    """
    return nx.cut_size(G,c1,c2,weight)*(1./nx.volume(c1,weight) + \
                                        1./nx.volume(c2,weight))

def conductance(G,c1,c2,weight=None):
    """Return the conductance between two containers of nodes c1 and c2.

    Conductance is defined by the cut size between two sets of nodes divided
    by the minimum volume of the c1 and c2/.[1]

    Parameters
    ----------
    G : NetworkX Graph
    c1, c2 : container
      container of nodes
    weight : keyword, optional default=None
      keyword for weight on edges

    Returns
    -------
    conductance : float

    See Also
    --------
    cut_size
    volume
    normalized_cut_size
    expansion

    References
    ----------
    ..[1] David Gleich. 'Heirarchicical Directed Spectral Graph Partitioning'. Website
          report. http://www.stanford.edu/~dgleich/publications/directed-spectral.pdf
    """
    return nx.cut_size(G,c1,c2,weight)/float(min(nx.volume(c1,weight),
                                                 nx.volume(c2,weight)))

def expansion(G, S1, S2, weight=None):
    """Return the edge expansion for G with node sets S1 and S2.

    Expansion is the cut size between two sets of nodes divided
    by the minimum of the sizes of U and V [1]_.

    Parameters
    ----------
    G : NetworkX Graph
    S1, S2 : container
      Container of nodes (e.g. set)
    weight : key
      Edge data key to use as weight.  If None, edge weights are set to 1.

    Returns
    -------
    expansion : float

    See Also
    --------
    cut_size
    volume
    conductance
    normalized_cut_size

    References
    ----------
    .. [1] Fan Chung, Spectral Graph Theory 
       (CBMS Regional Conference Series in Mathematics, No. 92), 
       American Mathematical Society, 1997, ISBN 0-8218-0315-8
       http://www.math.ucsd.edu/~fan/research/revised.html
    """
    return float(nx.cut_size(G, S1, S2, weight)) / min(len(S1), len(S2))

def community_performance(G,C):
    """Determine the performance of a community C on a
    graph G.

    Performance is the ratio of existing intra community edges
    plus no existant inter community edges and total possible edges.

    Parameters
    ----------
    G : NetworkX Graph
    C : list of sets
      Community Structure

    Returns
    -------
    P : float
      performance of the community

    Raises
    ------
    NetworkXError
      If C is not a partition of the graph

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> nx.community_performance(G,nx.spectral_partition(G))
    0.6149732603208558

    Notes
    -----
    Defined for all Graphs. If multigraph only counts multiplicity
    once.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174
       http://arxiv.org/abs/0906.0612 
    """

    if not nx.is_partition(G,C):
        raise NetworkXError("C is not a partition of G")
    P = 0.0
    aff = {}
    n = G.order()
    for i in G.nodes_iter():
        aff[i] = nx.affiliation(i,C)[0]
    for i in G.nodes_iter():
        for j in G.nodes_iter():
            if G.has_edge(i,j) and aff[i] ==aff[j]:
                P += 1
            elif (not G.has_edge(i,j)) and (not aff[i]==aff[j]):
                P += 1
    return P/(n*(n-1)) #This correct for both directed and undirected
                       #if G is undirected we count twice so divide by 2
                       #if G is dirceted we count once but there are twice
                       #as many edges 
        
def community_coverage(G,C):
    """Determine the coverage of a community C on a graph G.

    Coverage is defined as the ratio of intra-community edges to
    the total number of edges

    Parameters
    ----------
    G : NetworkXGraph
    C : list of sets
      Community Structure

    Returns
    -------
    P : float
      coverage of the community

    Raises
    -------
    NetworkXError
     If C is not a partion of the nodes of G

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> nx.community_coverage(G,nx.spectral_partition(G))
    0.8571428571428571

    Notes
    -----
    On MultiGraphs and MultiDiGraphs uses the multiplicity of
    edges.

    References
    ----------
    .. [1] Santo Fortunato 'Community Detection in Graphs' Physical Reports
       Volume 486, Issue 3-5 p. 75-174
       http://arxiv.org/abs/0906.0612
    """
    if not nx.is_partition(G,C):
        raise NetworkXError("C is not a partition of G")

    aff = {}
    for i in G.nodes_iter():
        aff[i] = nx.affiliation(i,C)[0]

    P = 0.0
    for (i,j) in G.edges_iter():
        if aff[i] == aff[j]:
            if G.is_multigraph():
                P += len(G.edge[i][j])
            else:
                P += 1
    return P/G.number_of_edges()
