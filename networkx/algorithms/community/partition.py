from copy import deepcopy
import random
import networkx as nx
#    Copyright(C) 2011 by
#    Ben Edwards <bedwards@cs.unm.edu>
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
__author__="""\n""".join(['Ben Edwards (bedwards@cs.unm.edu)',
                          'Aric Hagberg (hagberg@lanl.gov)'])



def spectral_modularity_partition(G):
    """Return a node partition based on the Modularity Matrix 
    eigenvectors.

    This method calculates the eigenvector v associated with the second
    largest eigenvalue of the Modularity Matrix. Where the Modularity Matrix
    is defined as

    ..math::
        B_{ij} = A_{ij} - \\frac{k_ik_j}{2m}

    where A is the adjacency matrix and k_i is the degree of node i, and m
    is the number of edges in the graph. Nodes are put in one partition if
    their corresponding value in the eigenvector is <0 and the other partition
    if it is >=0

    Parameters
    ----------
    G : NetworkX Graph

    Returns
    --------
    C : list of sets
      Spectral Modularity partition of the nodes in G

    Raises
    ------
    ImportError
      If NumPy is not available

    Examples
    --------
    >>> G = nx.karate_club_graph()
    >>> nx.spectral_partition(G)
    [set([0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 16, 17, 19, 21]),
     set([8, 9, 14, 15, 18, 20, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33])]


    Notes
    -----
    Defined for Graphs, DiGraphs, MultiGraphs, and MultiDiGraphs.

    References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', pages 373-378
       Oxford University Press 2011.
    """
    try:
        import numpy as np
    except:
        raise ImportError("spectral_partition() \
                           requires NumPy: http://scipy.org/")


    k = np.matrix(G.degree().values())
    m = G.number_of_edges()
    B = nx.adj_matrix(G) - (k.transpose()*k)/(2.0*m)
    eigenvalues,eigenvectors=np.linalg.eig(B)
    # sort and keep smallest nonzero 
    index=np.argsort(eigenvalues)[-1] # -1 index is largest eigenvalue
    v2 = zip(np.real(eigenvectors[:,index]),G)
    
    C = [set(),set()]
    
    for (u,n) in v2:
        if u < 0:
            C[0].add(n)
        else:
            C[1].add(n)
    return C
            
def greedy_max_modularity_partition(G,C_init=None,max_iter=10):
    """Partition a graph G into two communities using greedy modularity
    maximization.

    The algorithm works by selecting a node to change communities by
    which will maximize the modularity. The swap is made and the
    community structure with the highest modularity is kept.
    
    Parameters
    ----------
    G : NetworkX Graph
    C_init : list of sets option default (None)
      Community Partition
    max_iter : int
      Maximum number of times to attempt swaps
      to find an improvemement before giving up

    Returns
    -------
    C : list of sets
      Partition of the nodes of the graph

    Raises
    -------
    NetworkXError
      if C_init is not a valid partition of the
      graph into two communities or if G is a MultiGraph

    Examples
    --------
    >>> G = nx.barbell_graph(3,0)
    >>> nx.greedy_max_modularity_partition(G)
    [set([0,1,2]),set([3,4,5])]

    Notes
    -----
    Defined on all Graph, DiGraph, not defined for MultiGraph

    References
    ----------
    .. [1] M. E. J Newman 'Networks: An Introduction', pages 373-375
       Oxford University Press 2011."""

    if G.is_multigraph():
        raise nx.NetworkXError("greed_max_modularity() not defined for multigraph")
    if C_init is None:
        m1 = G.order()/2
        m2 = G.order()-m1
        C = nx.random_partition(G.nodes(),partition_sizes=[m1,m2])
    else:
        if not nx.is_partition(G,C_init):
            raise nx.NetworkXError("C_init doesn't partition G")
        if not len(C_init) == 2:
            raise nx.NetworkXError("C_init doesn't partition G into 2 communities")
        C = deepcopy(C_init)
            

    C_mod = nx.modularity(G,C)
    Cmax = deepcopy(C)
    Cnext = deepcopy(C)

    Cmax_mod = C_mod
    Cnext_mod = C_mod

    itrs = 0

    m = float(G.number_of_edges())
    while Cmax_mod >= C_mod and itrs < max_iter:
        C = deepcopy(Cmax)
        C_mod = Cmax_mod
        Cnext = deepcopy(Cmax)
        Cnext_mod = Cmax_mod
        ns = set(G.nodes())
        while ns:
            max_swap = -1.0
            max_node = None
            max_nod_comm = None
            dc =[sum(G.degree(Cnext[0]).values()), \
                 sum(G.degree(Cnext[1]).values())]
            for n in ns:
                n_comm = nx.affiliation(n,Cnext)[0]
                d_eii = -len(set(G.neighbors(n)).intersection(Cnext[n_comm]))/m
                d_ejj = len(set(G.neighbors(n)).intersection(Cnext[1-n_comm]))/m
                d_sum_ai = (G.degree(n)/(2*m**2))* \
                           (dc[n_comm]-dc[1-n_comm]-G.degree(n))
                swap_change = d_eii + d_ejj + d_sum_ai

                if swap_change > max_swap:
                    max_swap = swap_change
                    max_node = n
                    max_node_comm = n_comm
            Cnext[max_node_comm].remove(max_node)
            Cnext[1-max_node_comm].add(max_node)
            Cnext_mod += max_swap
            ns.remove(max_node)
            if Cnext_mod > Cmax_mod:
                Cmax = deepcopy(Cnext)
                Cmax_mod = Cnext_mod
        itrs += 1
    return C

def recursive_partition(G,
                        partition_function,
                        depth,
                        dendogram=False,
                        **kwargs):

    """Recursively partition the graph G using the
    the algorithm defined by partition function depth
    times.
    """
    C = [set(G)]
    if dendogram:
        D = nx.Graph()
    for _ in range(depth):
        C_next = []
        for c in C:
            C_next_add = partition_function(G.subgraph(c),**kwargs)
            if dendogram:
                D.add_edges_from(zip([frozenset(c)]*len(C_next_add),
                                     map(frozenset,C_next_add)))
            C_next += C_next_add
        C = deepcopy(C_next)
    if dendogram:
        return D
    else:
        return C
