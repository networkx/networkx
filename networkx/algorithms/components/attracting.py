# -*- coding: utf-8 -*-
"""
Attracting components.
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__authors__ = "\n".join(['Christopher Ellison'])
__all__ = ['number_attracting_components', 
           'attracting_components',
           'is_attracting_component', 
           'attracting_component_subgraphs',
           ]

def attracting_components(G):
    """Returns a list of attracting components in `G`.

    An attracting component in a directed graph `G` is a strongly connected
    component with the property that a random walker on the graph will never
    leave the component, once it enters the component.

    The nodes in attracting components can also be thought of as recurrent
    nodes.  If a random walker enters the attractor containing the node, then
    the node will be visited infinitely often.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    attractors : list
        The list of attracting components, sorted from largest attracting
        component to smallest attracting component.

    See Also
    --------
    number_attracting_components
    is_attracting_component 
    attracting_component_subgraphs

    """
    scc = nx.strongly_connected_components(G)
    cG = nx.condensation(G, scc)
    attractors = [scc[n] for n in cG if cG.out_degree(n) == 0]
    attractors.sort(key=len,reverse=True)
    return attractors


def number_attracting_components(G):
    """Returns the number of attracting components in `G`.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    n : int
        The number of attracting components in G.

    See Also
    --------
    attracting_components
    is_attracting_component
    attracting_component_subgraphs

    """
    n = len(attracting_components(G))
    return n


def is_attracting_component(G):
    """Returns True if `G` consists of a single attracting component.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    attracting : bool
        True if `G` has a single attracting component. Otherwise, False.

    See Also
    --------
    attracting_components
    number_attracting_components
    attracting_component_subgraphs

    """
    ac = attracting_components(G)
    if len(ac[0]) == len(G):
        attracting = True
    else:
        attracting = False
    return attracting


def attracting_component_subgraphs(G):
    """Returns a list of attracting component subgraphs from `G`.

    Parameters
    ----------
    G : DiGraph, MultiDiGraph
        The graph to be analyzed.

    Returns
    -------
    subgraphs : list
        A list of node-induced subgraphs of the attracting components of `G`.
    
    Notes
    -----
    Graph, node, and edge attributes are copied to the subgraphs.

    See Also
    --------
    attracting_components
    number_attracting_components
    is_attracting_component

    """
    subgraphs = [G.subgraph(ac).copy() for ac in attracting_components(G)]
    return subgraphs

