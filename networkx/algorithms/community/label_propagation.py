#-*- coding: utf-8 -*-
#    Copyright (C) 2015 
#    All rights reserved.
#    BSD license.


"""
Semi-synchronous label propagation community detection algorithm.
"""

from collections import Counter
import networkx as nx
from networkx.utils.decorators import not_implemented_for


__all__ = ["label_propagation_communities"]

@not_implemented_for('directed')
def label_propagation_communities(G):
    """Finds communities in graph using a semi-synchronous label propagation 
    method[1]_. This method combines the advantages of both the synchronous and  
    asynchronous models. Not implemented for directed graphs.
    
    Parameters
    ----------
    G : graph
    An undirected NetworkX graph.      
    
    Returns
    -------
    communities : list
    List of the communities (sets)
    
    Raises
    ------
    NetworkXNotImplemented
       If the graph is directed
  
    References
    ----------
    .. [1] Cordasco, G., & Gargano, L. (2010, December). Community detection 
       via semi-synchronous label propagation algorithms. In Business 
       Applications of Social Network Analysis (BASNA), 2010 IEEE International 
       Workshop on (pp. 1-8). IEEE.
    """
    coloring = _color_network(G)
    # Create a unique label for each node in the graph
    labeling = {v: k for k, v in enumerate(G)}
    while not _labeling_complete(labeling, G):
        # Update the labels of every node with the same color.
        for color, nodes in coloring.items():
            for n in nodes:
                _update_label(n , labeling, G)
        
    for label in set(labeling.values()):
        yield set((x for x in labeling if labeling[x] == label))
        
def _color_network(G):
    """Colors the network so that neighboring nodes all have distinct colors.
       Returns a dict of set of nodes and also a lookup of nodes to colors, in 
       a tuple in that order.
    """
    coloring = dict() # color => set(node)
    colors = nx.coloring.greedy_color(G)
    for node, color in colors.items():
        if color in coloring:
            coloring[color].add(node)
        else:
            coloring[color] = set([node])
            
    return coloring

def _labeling_complete(labeling, G):
    """Determines whether or not LPA is done. It is complete when all nodes 
       have a label that is in the set of highest frequency labels amongst its
       neighbors.

       Nodes with no neighbors are themselves a community and are therefore
       labeled.
    """    
    return all(labeling[v] in 
                    _most_frequent_labels(v, labeling, G) 
                        for v in G if len(G[v]) > 0)

def _most_frequent_labels(node, labeling, G):
    """Finds all labels of maximum frequency. Specified freqs must be a mapping
       from label to frequency of that label.          

       Returns a set.
    """   
    if not G[node]: 
        # Nodes with no neighbors are themselves a community and are labeled
        # accordingly, hence the immediate if statement.
        return {labeling[node]}

    # Compute the frequencies of all neighbours of node    
    freqs = Counter(labeling[q] for q in G[node])
    max_freq = max(freqs.values())
    return {label for label, freq in freqs.items() if freq == max_freq}        

           
def _update_label(node, labeling, G):
    """Updates the label of a node using the Prec-Max tie breaking 
       algorithm, as explained in: 'Community Detection via Semi-Synchronous 
       Label Propagation Algorithms' Cordasco and Gargano, 2011
    """
    high_labels = _most_frequent_labels(node, labeling, G)
    if len(high_labels) == 1:
        labeling[node] = high_labels.pop()
    elif len(high_labels) > 1:
        # Prec-Max
        labeling[node] = labeling[node] if labeling[node] in high_labels else max(high_labels)
