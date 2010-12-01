# -*- coding: utf-8 -*-
"""
This module implements routines to approximate a graph by a chordal partial k-tree. 
"""
__authors__ = "\n".join(['Jesus Cerquides <cerquide@iiia.csic.es>'])
#    Copyright (C) 2010 by 
#    Jesus Cerquides <cerquide@iiia.csic.es>
#    All rights reserved.
#    BSD license.

__all__ = ['single_source_retriangulate',
           'incremental_treewidthbounded_approximation',
           'incremental_approximation_cliqueset'
           ]

import networkx as nx
import random

def single_source_retriangulate(G,s,t,treewidth_bound=1e90):
    """
    G is a chordal graph.
    This function returns a new graph after adding (s,t) to 
    G and retriangulating it from s.
    If a treewidth_bound is provided, it returns None 
    if the retriangulation exceeds the treewidth_bound
    """
    try:
        (I,h) = nx.induced_nodes(G,s,t,treewidth_bound)
        return h
    except nx.NetworkXError:
        return None


def incremental_treewidthbounded_approximationCC(G,treewidth_bound,retriangulation_function):
    """
    Same as incrementalTreewidthBoundedApproximation but requires G to be CONNECTED 
    """
    edges = G.edges()
    random.shuffle(edges)
    H = nx.Graph()
    H.add_nodes_from(G.nodes())
    for (s,t) in edges:
        if not H.has_edge(s,t):
            #print (s,t)
            newH = retriangulation_function(H,s,t,treewidth_bound)
            if newH != None:
                H = newH
                #print (s,t)," has been added"
                #print H.edges()
            else:
                #print (s,t)," has been rejected"
                pass
                #print "Too much"
    return H

def incremental_treewidthbounded_approximation(G,treewidth_bound,retriangulation_function):
    """
    Given a graph G, a treewidthBound , and a retriangulationFunction, 
    this function constructs a chordal graph that is a partial treewidthBound-tree
    by succesively adding edges 
    from G until any additional edge will make the treewidth larger than  
    the bound.
    The retriangulationFunction should have the same interface that 
    "singleSourceRetriangulate".
    """
    H = nx.Graph()
    for CC in nx.algorithms.components.connected.connected_component_subgraphs(G):
        hCC = incremental_treewidthbounded_approximationCC(CC,treewidth_bound,retriangulation_function)
        H = nx.union(H,hCC)
    return H
  
def incremental_approximation_cliqueset(G,treewidth_bound,retriangulation_function):
    """
    Given a graph G, a treewidthBound , and a retriangulationFunction, 
    this function constructs a chordal graph that is a partial treewidthBound-tree
    by succesively adding edges from G until any additional edge will 
    make the treewidth larger than the bound. Then it generates and returns 
    the list of maximal cliques of this partial treewidthBound-tree.
    
    The retriangulationFunction should have the same interface that 
    "singleSourceRetriangulate".
    """
    H = nx.incremental_treewidthbounded_approximation(G,treewidth_bound,retriangulation_function)
    return nx.chordal_graph_cliques(H)


