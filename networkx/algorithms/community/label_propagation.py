#-*- coding: utf-8 -*-
#    Copyright (C) 2015 
#    All rights reserved.
#    BSD license.


"""
Semi-synchronous label propagation algorithm for community detection.
"""

from networkx.utils.decorators import not_implemented_for
from collections import Counter
from itertools import groupby


__all__ = ["label_propagation_communities"]


@not_implemented_for('directed')
def label_propagation_communities(G):
    """Finds communities in graph using the label propagation method[1]_. This
    method uses the diffusion of information in the network to identify
    communities. Not implemented for directed graphs.
    
    Parameters
    ----------
    G : graph
    An undirected NetworkX graph.      
    
    Returns
    -------
    communities : list
    List of the communities (sets) 
    
  
    References
    ----------
    .. [1] Cordasco, G., & Gargano, L. (2010, December). Community detection 
       via semi-synchronous label propagation algorithms. In Business 
       Applications of Social Network Analysis (BASNA), 2010 IEEE International 
       Workshop on (pp. 1-8). IEEE.
    """
    coloring = _color_network(G)
    labeling = _uniquely_label(G)
    nrounds = 1
    while not _labeling_complete(labeling, G):
        nrounds += 1
        _update_labels(labeling, coloring, G)
        
    for label in set(labeling.values()):
        yield set((x for x in labeling if labeling[x] == label))
    
    
def _break_color_tie(current, labels):
    """Uses Prec-Max tie-breaking to break the ties, as laid out in:
       'Community Detection via Semi-Synchronous Label Propagation Algorithms'
       Cordasco and Gargano, 2011

       If the labels set specified is empty than the current label is returned.

       Specified set of labels is assummed to be one of integers.
    """
    if len(labels) == 0 or current in labels:
        new_label = current
    else:
        new_label = max(labels)
    return new_label


def _calculate_label_frequencies(node, labeling, G):
    """Counts up the labels of the neighbors of the specified node. Returns a
       dictionary from the label to the frequency.
    """
    return dict(Counter(labeling[q] for q in G[node]))


def _color_network(G):
    """Colors the network so that neighboring nodes all have distinct colors.
       Returns a dict of set of nodes and also a lookup of nodes to colors, in 
       a tuple in that order.
    """
    coloring = dict() # color => set(node)
    lookup = dict() # node => color
    finally_colored_nodes = set()
    
    for n in G.nodes():
        if n not in lookup:
            color = 0                 
        else:
            color = lookup[n]
        lookup[n] = color
        finally_colored_nodes.add(n)
        if color not in coloring: 
            coloring[color] = set()
        coloring[color].add(n)
        for q in G.neighbors(n):
            if q not in finally_colored_nodes: 
                lookup[q] = lookup[n] + 1
    
    return coloring


def _form_communities(labeling, G):
    """Determines the communities from the labels of the network, returning a
       dict of sets of nodes.
    """
    return {k: set(v) 
            for k, v in groupby(sorted(G, key=labeling.get), key=labeling.get)}


def _labeling_complete(labeling, G):
    """Determines whether or not LPA is done. It is complete when all nodes 
       have a label that is in the set of highest frequency labels amongst its
       neighbors.

       Nodes with no neighbors are themselves a community and are therefore
       labeled, hence the immediate if statement in the for loop.
    """    
    return all(labeling[v] in 
                    _select_labels_of_highest_frequency(v, labeling, G) 
                        for v in G if len(G[v]) > 0)


def _select_labels_of_highest_frequency(node, labeling, G):
    """Finds all labels of maximum frequency. Specified freqs must be a mapping
       from label to frequency of that label.

       Returns a set.
    """
    freqs = _calculate_label_frequencies(node, labeling, G)
    max_freq = max(freqs.values())
    return {label for label, freq in freqs.items() if freq == max_freq}


def _uniquely_label(G):
    """Gives a unique label (integer) to each node in the network."""
    return {n : label for n, label in zip(G.nodes(), range(len(G)))}


def _update_labels(labeling, coloring, G):
    """Updates labels of every single node in the network."""
    for color, nodes in coloring.items():
        for n in nodes:
            _update_label(n , labeling, G)


def _update_label( node, labeling, G):
    """Updates the label of a SINGLE node in the network."""
    high_labels = _select_labels_of_highest_frequency(node, labeling, G)
    if len(high_labels) == 1:
        labeling[node] = high_labels.pop()
    elif len(high_labels) > 1:
        labeling[node] = _break_color_tie(labeling[node] , high_labels)
