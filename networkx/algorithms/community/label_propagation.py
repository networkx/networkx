# -*- coding: utf-8 -*-
"""
Created on Thu Oct 02 14:03:50 2014
Based on the code donated by Tyler Rush 
(https://github.com/networkx/networkx/issues/617)

LPA community detection algorithm (based off of 'Community Detection via 
Semi-Synchronous Label Propagation Algorithms' Cordasco and Gargano, 2011

@author: Aitor Almeida <aitoralmeida@gmail.com>
All rights reserved.
BSD license.
"""

from networkx.utils.decorators import not_implemented_for

__author__ = """Aitor Almeida <aitoralmeida@gmail.com"""
__all__ = ["label_propagation_communities"]

@not_implemented_for('directed')
def label_propagation_communities(G):
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
    counts = dict()
    for q in G.neighbors(node):
        qlabel = labeling[q]
        if qlabel not in counts:
            counts[qlabel] = 1 
        else:
            counts[qlabel] += 1              
    return counts

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
    communities = dict() # label => set(nodes)
    for n in G.nodes():
        label = labeling[n]
        if label not in communities: 
            communities[label] = set()
        communities[label].add(n)
    return communities

def _labeling_complete(labeling, G):
    """Determines whether or not LPA is done. It is complete when all nodes 
       have a label that is in the set of highest frequency labels amongst its
       neighbors.

       Nodes with no neighbors are themselves a community and are therefore
       labeled, hence the immediate if statement in the for loop.
    """
    result = True
    for node in G:
        if len(G.neighbors(node)) != 0:
            counts = _calculate_label_frequencies(node, labeling, G)
            high_labels = _select_labels_of_highest_frequency(counts)
            if labeling[node] not in high_labels: 
                result = False
                break
    return result

def _select_labels_of_highest_frequency(freqs):
    """Finds all labels of maximum frequency. Specified freqs must be a mapping
       from label to frequency of that label.

       Returns a set.
    """
    labels = set()
    mx = -1000000
    for label, freq in freqs.items():
        if mx <= freq:
            if mx < freq:
                mx = freq
                labels.clear()
        labels.add( label )
    return labels


def _uniquely_label(G):
    """Gives a unique label (integer) to each node in the network."""
    labeling = dict()
    for n, label in zip(G.nodes(), range(len(G))):
        labeling[n] = label
    return labeling

def _update_labels(labeling, coloring, G):
    """Updates labels of every single node in the network."""
    for color, nodes in coloring.items():
        for n in nodes:
            _update_label(n , labeling, G)

def _update_label( node, labeling, G):
    """Updates the label of a SINGLE node in the network."""
    counts = _calculate_label_frequencies(node, labeling, G)
    high_labels = _select_labels_of_highest_frequency(counts)
    if len(high_labels) == 1:
        labeling[node] = high_labels.pop()
    elif len(high_labels) > 1:
        labeling[node] = _break_color_tie(labeling[node] , high_labels)