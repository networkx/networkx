# -*- coding: utf-8 -*-
"""
Algorithm to find a maximum clique.

"""
#    Peng Feifei <pengff@ios.ac.cn>
#    All rights reserved.
#    BSD license.

import networkx as nx
__author__ = """Peng Feifei (pengff@ios.ac.cn)"""
__all__ = ['maxclique_set']

def maxclique_set(G):
    """Finds a maximum clique set for the graph G.

    A clique in an undirected graph G = (V, E) is a subset of the vertex set
    `C \subseteq V`, such that for every two vertices in C, there exists an edge
    connecting the two. This is equivalent to saying that the subgraph
    induced by C is complete (in some cases, the term clique may also refer
    to the subgraph).

    A maximum clique is a clique of the largest possible size in a given graph.
    The clique number `\omega(G)` of a graph G is the number of
    vertices in a maximum clique in G. The intersection number of
    G is the smallest number of cliques that together cover all edges of G.

    http://en.wikipedia.org/wiki/Maximum_clique

    Parameters
    ----------
    G : NetworkX graph
        Undirected graph

    Returns
    -------
    maxcset : Set
        The maximum clique

    Notes
    -----
    This function is an implementation of algorithm 7 in [1] which
    finds a maximum clique for an undirected graph.

    References
    ----------
    .. [1] Carraghan R, Pardalos P M. An exact algorithm for the 
           maximum clique problem[J]. Operations Research Letters, 1990, 9(6): 375-382.

    """
    if G is None:
        raise ValueError("Expected NetworkX graph!")
    #order nodes by increasing edge density. say v_1,v_2,...,v_n. generally v_k is a vertex 
    #of smallest degree in G-{v_1,...,v_k-1}. 
    nodes=[]
    H=G.copy()
    while G.nodes()!=[]:
        node=sorted(G.nodes(),key=G.degree)[0]
        nodes.append(node)
        G.remove_node(node)
    G=H
    
    maxcset=[]
    currD = 1
    start = [None]*(2*(len(nodes)+1))
    last  = [None]*(2*(len(nodes)+1))
    ADJ=[[]]*(2*(len(nodes)+1))
    ADJ[1]=nodes
    start[1]=0
    last[1]=len(nodes)
    while True:
        start[currD]+=1
        if currD==1 and currD+last[currD]-start[currD]<=len(maxcset): 
                break
        #determine node for next depth
        if currD+last[currD]-start[currD]>len(maxcset):
            dtemp=currD
            currD+=1
            start[currD]=0
            last[currD]=0
            for i in ADJ[dtemp]:
                if (ADJ[dtemp][start[dtemp]-1],i) in G.edges() or (i,ADJ[dtemp][start[dtemp]-1]) in G.edges():
                    ADJ[currD]=ADJ[currD]+[i]
                    last[currD]+=1
            
            # if the next depth does not contain any nodes, see if a new maxclique has been found and return to 
            #previous depth.  
            if last[currD]==0:
                ADJ[currD]=[]
                currD=currD-1
                if currD>len(maxcset):
                    tem=[]
                    for i in range(1,currD+1):
                        tem.append(ADJ[i][start[i]-1])
                    maxcset=tem
        else:
                #prune, further expansion would not find a better result.
                ADJ[currD]=[]
                currD=currD-1 
    # return the maximum clique found in graph           
    return maxcset

