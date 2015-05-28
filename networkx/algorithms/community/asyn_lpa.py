# -*- coding: utf-8 -*-
#    Copyright (C) 2015
#    All rights reserved.
#    BSD license.

import random
import networkx as nx

def asyn_lpa_communities(G, weight=None):
    """
    Asynchornous label propagation algorithm for community detection described
    on [1]_.
    
    Parameters
    ----------
    G : graph
        Network to be processed
        
    weight : string
        If the graph is weighted, the edge parameter representing the weight
         
    Returns
    -------
    communities : list
        List of communities (sets)
    
    References
    ----------
    .. [1] Raghavan, Usha Nandini, Réka Albert, and Soundar Kumara. "Near
           linear time algorithm to detect community structures in large-scale
           networks." Physical Review E 76.3 (2007): 036106.
    """
    
    labels = {n : n for n in G}
    cont = True 
    while cont:
        cont = False
        nodes = nx.nodes(G)
        random.shuffle(nodes)
        # Calculate the label for each node
        for node in nodes:
            n_neighbors = nx.neighbors(G, node)
            
            if len(n_neighbors) < 1:
                continue
            
            label_freq = {}            
            # Get label frecuencies
            for neighbor in n_neighbors:
                n_label = labels[neighbor]
                if n_label in label_freq:
                    if weight:                    
                        label_freq[n_label] = label_freq[n_label] + G.edge[neighbor][node][weight]
                    else:
                        label_freq[n_label] += 1                
                else:
                    if weight:                    
                        label_freq[n_label] = G.edge[neighbor][node][weight]
                    else:
                        label_freq[n_label] = 1   
                        
            # Chose the label with the highest frecuency
            # If more than 1 label has the highest frecuency choose one 
            # randomly
            max_freq = max(label_freq.values())
            best_labels = [label for label, freq in label_freq.items() if freq == max_freq]
            new_label = random.choice(best_labels)
            labels[node] = new_label
            # Continue until all nodes have a label that is best than other 
            # neighbour labels
            cont = cont or not (len(best_labels) == 1)
            
    
    #return the communities        
    communities = {l for l in labels.values()}
    for c in communities:
        yield {n for n in labels if labels[n] == c}