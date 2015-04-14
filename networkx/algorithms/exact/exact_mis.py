# -*- coding: utf-8 -*-
"""
Algorithm to find a maximum independent set.

"""
#    Peng Feifei <pengff@ios.ac.cn>
#    All rights reserved.
#    BSD license.

import networkx as nx
import exact_clique
__author__ = """Peng Feifei (pengff@ios.ac.cn)"""
__all__ = ['maximum_independent_set']

def maximum_independent_set(G):
    """Finds a maximum clique set for the graph G.

    Independent set or stable set is a set of vertices in a graph, no two of
    which are adjacent. That is, it is a set I of vertices such that for every
    two vertices in I, there is no edge connecting the two. Equivalently, each
    edge in the graph has at most one endpoint in I. The size of an independent
    set is the number of vertices it contains.

    A maximum independent set is a largest independent set for a given graph G
    and its size is denoted α(G). The problem of finding such a set is called
    the maximum independent set problem and is an NP-hard optimization problem.
    As such, it is unlikely that there exists an efficient algorithm for finding
    a maximum independent set of a graph.

    http://en.wikipedia.org/wiki/Independent_set_(graph_theory)

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    iset : Set
        The maximum independent set

    Notes
    -----
    Maximum independent set algorithm is based on [1]:

    References
    ----------
    .. [1] Carraghan R, Pardalos P M. An exact algorithm for the 
           maximum clique problem[J]. Operations Research Letters, 1990, 9(6): 375-382.

    """
    if G is None:
        raise ValueError("Expected NetworkX graph!")
    cgraph = nx.complement(G)
    iset=exact_clique.maxclique_set(cgraph)
    return iset

def main():
   G=nx.Graph()
   # G.add_edges_from([(1,2),(1,4),(1,5),(2,3),(2,4),(2,6),(2,7),(3,4),(3,7),(3,8),(4,5),(4,6)
   #  ,(4,7),(4,8),(5,6),(6,7),(6,8)])
   G.add_edges_from([(1,2),(1,3),(2,3),(2,4),(3,4)])
   maxiset=maximum_independent_set(G)
   print maxiset
   A=[[]]*5
   A[2].append(3)
          
if __name__ == '__main__':
    main()

