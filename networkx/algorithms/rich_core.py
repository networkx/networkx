# -*- coding: utf-8 -*-
#    Copyright (C) 2017 by
#    Iacopo Iacopini <i.iacopini@qmul.ac.uk>
#    All rights reserved.
#    BSD license.
#
# Authors: Iacopo Iacopini (i.iacopini@qmul.ac.uk)
"""Function for extracting the rich-core of a network,
as defined by Ma A and Mondragón RJ (2015) in Rich-cores in networks. PLoS One 10(3):e0119678."""


import networkx as nx
from networkx.utils import accumulate
from networkx.utils import not_implemented_for

__all__ = ['extract_rich_core']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def extract_rich_core(G, weight='weight'):
    """Returns the core/periphery structure of a weighted undirected network (see [1]).
        
        Args
        ----
        G: NetworkX weighted undirected graph.
        
        weight: string (default='weight')
        Key for edge data used as the edge weight w_ij.
        
        Returns
        -------
        sigmas: list
        List of σ_i values associated to each node i of the network, representing the strength of the node i
        after rescaling the weights in units of the minimal weight. σ_i = ∑j⌈w_ij/w_min⌉
        
        ranked_nodes: list
        List of nodes ranked by normalised strength σ_i.
        
        r_star: int
        r_star (r∗) is the index of the core boundary node, such that σ^{+}_r∗>σ^{+}_r for r > r*, where
        σ^{+}_i is the portion of σ_i that connects node i, ranked r, to nodes of a higher rank.
        
        
        References
        ----------
        .. [1] Ma A and Mondragón RJ (2015).
        "Rich-cores in networks".
        PLoS One 10(3):e0119678.
        
        """
    
    
    G = G.to_undirected()
    
    #Looking for the minimal weight
    weights = [e[2][weight] for e in G.edges_iter(data=True)]
    minw = min(weights)
    
    #Normalising by the minimal weight
    for e in G.edges_iter(data=True):
        i = e[0]
        j = e[1]
        wij = e[2][weight]
        G[i][j][weight]=1.*wij/minw
    
    #Ranking the nodes in units of the minimal weight (by normalised strength)
    strength = G.degree(weight=weight)
    ranked_nodes = sorted(strength, key=strength.get, reverse=True)
    
    sigmas=[]
    for i in ranked_nodes:
        sigma_i=0
        for j in G.neighbors(i):
            if strength[j]>strength[i]:
                sigma_i += strength[j]
            else: continue
        sigmas.append(sigma_i)
    
    r_star = sigmas.index(max(sigmas))
    
    return sigmas, ranked_nodes, r_star