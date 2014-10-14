# -*- coding: utf-8 -*-
"""
Created on Thu Oct 09 16:31:16 2014

Bases on the algorithm described in:
  - Girvan, Michelle, and Mark EJ Newman. "Community structure in social and 
    biological networks." Proceedings of the National Academy of Sciences 99.12 
    (2002): 7821-7826.
  - Newman, Mark EJ, and Michelle Girvan. "Finding and evaluating community 
    structure in networks." Physical review E 69.2 (2004): 026113.
  - http://en.wikipedia.org/wiki/Girvan%E2%80%93Newman_algorithm

The community structure finding algorithm follows this steps:
    1.- Calculate the betweenness for all the edges
    2.- Find the edge with the highest score and remove it from the network
    3.- Recalculate the betweenness
    4.- Repeat from 2 until there are no more edges
    
The result is a dendogram where the leaves are the individual nodes.

The algorithm works on undirected networks with only a single node type and 
does not take it account edge weights.

@author: Aitor Almeida (aitoralmeida@gmail.com)
All rights reserved.
BSD license.
"""
import networkx as nx
from networkx.utils.decorators import not_implemented_for

__author__ = """Aitor Almeida (aitoralmeida@gmail.com)"""
__all__ = ["girvan_newman_communities"]

@not_implemented_for('directed')
def girvan_newman_communities(original_graph, preserve_original = True):    
    # The algorithm is divisive and the edges of the graph are going to be 
    # deleted. preserve_original allows to make a copy of the original graph so 
    # it is not destroyed, but this way the algorithm uses more memory.    
    
    if len(original_graph) < 2:
        raise nx.NetworkXError('''there must be more than one node to find 
                                communities''')
         
    if preserve_original:
        G = original_graph.copy()
    else:
        G = original_graph        
    return _girvan_newman_communities_rec(G)    
    
def _girvan_newman_communities_rec(G):    
    # Recursively find the communities in the graph. The final result is a 
    # dendogram where the leaves are the individual nodes.
    
    # 1.- Calculate the betweenness for all the edges
    connected_components = list(nx.connected_component_subgraphs(G))
    
    # Repeat until new communities are found
    while len(connected_components) < 2: 
        # 2.- Find the edge with the highest score and remove it 
        #     from the network
        _remove_highest_betweenness_edge(G)
        # 3.- Recalculate the betweenness
        connected_components = list(nx.connected_component_subgraphs(G))
        
    for component in connected_components:
        yield component.nodes()
        # 4.- Repeat from 2 until there are no more edges
        if component.size() != 0:            
            for x in _girvan_newman_communities_rec(component):
                yield x

def _remove_highest_betweenness_edge(G):
    # Finds the edge with the highest node betweenness centrality and removes
    # it from the graph. If a several nodes have the same betweenness edge 
    # value one of them is selected randomly (not actually random, depends on 
    # how the max built-in shorts the items).
    
    # Find highest betweenness edge   
    edge_betweenness = nx.edge_betweenness_centrality(G)
    highest_betweenness_edge = max(edge_betweenness, key=edge_betweenness.get)
    
    # Remove the edge
    G.remove_edge(*highest_betweenness_edge)    

            
