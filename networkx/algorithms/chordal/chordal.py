# -*- coding: utf-8 -*-
"""
This module implements routines related to chordal graphs. 
"""
__authors__ = "\n".join(['Jesus Cerquides <cerquide@iiia.csic.es>'])
#    Copyright (C) 2010 by 
#    Jesus Cerquides <cerquide@iiia.csic.es>
#    All rights reserved.
#    BSD license.

__all__ = ['is_chordal',
           'induced_nodes', 
           'chordal_graph_cliques',
           'chordal_graph_treewidth']

import networkx as nx
import random


def is_chordal(G):
    """Returns True if G is a chordal graph."""
    if len(_find_chordality_breaker(G))==0:
        return True
    else:
        return False


def chordal_graph_cliques(G):
    """Returns the set of maximal cliques of a chordal graph."""
    cliques = set()
    for C in nx.connected.connected_component_subgraphs(G):
        cliques |= _connected_chordal_graph_cliques(C)
        
    return cliques


def chordal_graph_treewidth(G):
    """Returns the treewidth of a chordal graph."""
    max_clique = -1
    for clique in nx.chordal_graph_cliques(G):
        max_clique = max(max_clique,len(clique))
    return max_clique - 1


def _is_complete_graph(G):
    """Returns True if G is a complete graph."""
    if G.number_of_selfloops()>0:
        raise nx. NetworkXError("Self loop found in _is_complete_graph()")
    n = G.number_of_nodes()
    if n < 2:
        return True
    e = G.number_of_edges()
    max_edges = ((n * (n-1))/2)
    return e == max_edges


def _find_missing_edge(G):
    """ Given a non-complete graph G, returns a missing edge."""
    nodes=set(G)
    for u in G:
        missing=nodes-set(G[u].keys()+[u])
        if missing:
            return (u,missing.pop())


def _max_cardinality_node(G,choices,wanna_connect):
    """Returns a set of node in choices that has more connections in G 
    to nodes in wanna_connect.
    """
    max_number = None 
    for x in choices:
        number=len([y for y in G[x] if y in wanna_connect])
        if number > max_number:
            max_number = number
            max_cardinality_node = x 
    return max_cardinality_node


def _find_chordality_breaker(G,s=None,treewidth_bound=float('inf')):
    """ Given a graph G, starts a max cardinality search 
    (starting from s if s is given and from a random node otherwise)
    trying to find a non-chordal cycle. 

    If it does find one, it returns (u,v,w) where u,v,w are the three
    nodes that together with s are involved in the cycle.
    """
    unnumbered = set(G)
    if s is None:
        s = random.choice(list(unnumbered))
    unnumbered.remove(s)
    numbered = set([s])
    current_treewidth = None
    while unnumbered:# and current_treewidth <= treewidth_bound:
        v = _max_cardinality_node(G,unnumbered,numbered)
        unnumbered.remove(v)
        numbered.add(v)
        clique_wanna_be = set(G[v]) & numbered
        sg = G.subgraph(clique_wanna_be)
        if _is_complete_graph(sg):
            # The graph seems to be chordal by now. We update the treewidth
            current_treewidth = max(current_treewidth,len(clique_wanna_be))
            if current_treewidth > treewidth_bound:
                raise nx.NetworkXError(\
                    "treewidth_bound exceeded: %s"%current_treewidth)
        else:
            # sg is not a clique,
            # look for an edge that is not included in g
            (u,w) = _find_missing_edge(sg)
            return (u,v,w)
    return ()
    

def induced_nodes(G,s,t,treewidth_bound=float('inf')):
    """G is a chordal graph and s,t is an edge that is not in G. 

    Returns a pair (I,H) where I is the set of induced nodes in the
    path from s to t and H is the graph G plus (s,t) and an edge from
    s to every induced node in I. 

    If a treewidth_bound is provided, the search for induced nodes will end 
    as soon as the treewidth is exceeded.
    """
    H = nx.Graph(G)
    H.add_edge(s,t)
    I = set()
    triplet =  _find_chordality_breaker(H,s,treewidth_bound)
    while triplet:
        (u,v,w) = triplet
        I.update(triplet)
        for n in triplet:
            if n!=s:
                H.add_edge(s,n)
        triplet =  _find_chordality_breaker(H,s,treewidth_bound)
    if I:
        # Add t and the second node in the induced path from s to t.
        I.add(t)
        for u in G[s]: 
            if len(I & set(G[u]))==2:
                I.add(u)
                break
    return I,H

  
def _connected_chordal_graph_cliques(G):
    """Return the set of maximal cliques of a connected chordal graph."""
    if G.number_of_nodes() == 1:
        x = frozenset(G.nodes())
        return set([x])
    else:
        cliques = set()
        unnumbered = set(G.nodes())
        v = random.choice(list(unnumbered))
        unnumbered.remove(v)
        numbered = set([v])
        clique_wanna_be = set([v])
        while unnumbered:
            v = _max_cardinality_node(G,unnumbered,numbered)
            unnumbered.remove(v)
            numbered.add(v)
            new_clique_wanna_be = set(G.neighbors(v)) & numbered
            sg = G.subgraph(clique_wanna_be)
            if _is_complete_graph(sg):
                new_clique_wanna_be.add(v)
                if not new_clique_wanna_be >= clique_wanna_be:
                    cliques.add(frozenset(clique_wanna_be))
                clique_wanna_be = new_clique_wanna_be
            else:
                raise Exception("Graph is not chordal.")
        cliques.add(frozenset(clique_wanna_be))
        return cliques




