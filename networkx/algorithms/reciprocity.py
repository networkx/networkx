# -*- coding: utf-8 -*-
#
#    Copyright (C) 2015 by 
#    Haochen Wu <wuhaochen42@gmail.com>
#    All rights reserved.
#    BSD license.
"""Algorithms to calculate reciprocity in a directed graph."""
from itertools import combinations

import networkx as nx
from networkx import NetworkXError
from ..utils import not_implemented_for

__author__ = """\n""".join(['Haochen Wu <wuhaochen42@gmail.com>'])

__all__= ['reciprocity','overall_reciprocity']

@not_implemented_for('undirected','multigraph')
def reciprocity(G, nodes=None):
    """Computer the reciprocity in a directed graph.

    Parameters
    ----------
    G : graph
       A networkx directed graph
    nodes : container of nodes, optional (default=None)
       Compute reciprocity for nodes in this container.
       If remains unspecified, it will compute the reciprocity of the graph instead.

    Returns
    -------
    out : dictionary
       Reciprocity keyed by node label.
    
    """
    # If `nodes` is not specified, calculate the reciprocity of the graph.
    if nodes is None:
        return overall_reciprocity(G)

    # If `nodes` represents a single node in the graph, return only its
    # reciprocity.
    if nodes in G:
        return next(_reciprocity_iter(G,nodes))[1]

    # Otherwise, `nodes` represents an iterable of nodes, so return a
    # dictionary mapping node to its reciprocity.
    return dict(_reciprocity_iter(G,nodes))

def _reciprocity_iter(G,nodes):
    """ Return an iterator of (node, reciprocity).  

    """
    n = G.nbunch_iter(nodes)
    for node in n:
        pred = set(G.predecessors(node))
        succ = set(G.successors(node))
        overlap = pred & succ
        n_total = len(pred) + len(succ)
        if n_total == 0:
            raise NetworkXError('Not defined for isolated nodes.')
            
        reciprocity = 2*len(overlap)/float(n_total)
        yield (node,reciprocity)
        
@not_implemented_for('undirected','multigraph')
def overall_reciprocity(G):
    """Computer the reciprocity for the whole graph.

    Parameters
    ----------
    G : graph
       A networkx graph
    
    """
    n_all_edge = G.number_of_edges()
    n_overlap_edge = (n_all_edge - G.to_undirected().number_of_edges()) *2

    if n_all_edge == 0:
        raise NetworkXError("Not defined for empty graphs")

    return n_overlap_edge/float(n_all_edge)