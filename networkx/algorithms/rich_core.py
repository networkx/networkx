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
from collections import OrderedDict
from networkx.utils import not_implemented_for
from __future__ import division

__all__ = ['extract_rich_core']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def extract_rich_core(G, weight='weight'):
    r"""Returns the core/periphery structure of a the weighted undirected
    graph `G` as in [1]_.
    
    The *rich-core* of a network comes from the theoretical coupling the
    underlying principle of a *rich-club* with the escape time of a
    random walker. A $\sigma_i$ is associated to each node $i$ of the
    network, representing the strength of the node after rescaling the
    weights in units of the minimal weight:
    
    .. math::
    
        \sigma_i = \sum_j \frac{w_ij}{w_{min}}
    
    The *core boundary* node, separating the core from the periphery,
    is ranked as $r_{∗}$, such that $\sigma^{+}_{r_{∗}}>\sigma^{+}_{r}
    for $r>r_{∗}$, where $\sigma^{+}_i$ is the portion of $\sigma_i$ that
    connects node $i$, ranked $r$, to nodes of a higher rank.
    
    Parameters
    ----------
    G : NetworkX graph
        Weighted undirected graph.    
    weight : string (default='weight')
        Key for edge data used as the edge weight w_ij.
        
    Returns
    -------
    sigmas: dictionary
        Ordered dictionary (collection.OrderedDict) of nodes with the
        $\sigma$ as the value, representing the strength of the node after
        rescaling the weights in units of the minimal weight.
        
    node_max_sigma: node
        The core boundary node.
        
    Note
    ----
    Since the sigmas dictionary is ordered, the values can be directly
    plotted as plt.plot(sigmas.values()) to obtain the plot of Figure 3
    of [1]_.
      
    References
    ----------
    .. [1] Ma A and Mondragón RJ (2015),
       "Rich-cores in networks".
       PLoS One 10(3):e0119678.
    """
    if nx.is_directed(G):
        raise Exception('rich_core is not implemented for directed graphs.')    
   
    #Looking for the minimal weight
    minw = min(wt for u, v, wt in G.edges.data(weight))
    
    #Normalising by the minimal weight (adding a new attribute)
    for u, v, wt in G.edges.data(weight):
        G[u][v]['norm_weight']=wt/minw
    
    #Ranking the nodes in units of the minimal weight (by normalised strength)
    norm_strength = G.degree(weight='norm_weight')
    ranked_nodes = [n[0] for n in sorted(norm_strength, key=lambda x: x[1], reverse=True)]
    
    sigmas=OrderedDict()
    for i in ranked_nodes:
        sigma_i=0
        for j in G.neighbors(i):
            if norm_strength[j]>norm_strength[i]:
                sigma_i += norm_strength[j]
            else: continue
        sigmas[i]=sigma_i
    
    max_sigma = max(sigmas.values())
    node_max_sigma = [k for k, v in sigmas.items() if v == max_sigma]
    
    return sigmas, node_max_sigma
