# -*- coding: utf-8 -*-
"""
************
Clustering Coefficient
************

Given a graph `G = (V, E)`, approximate the fraction of triangles that exist over the total number of triangles

http://en.wikipedia.org/wiki/Clustering_coefficient
"""
#   Copyright (C) 2013 by
#   Fred Morstatter <fred.morstatter@asu.edu>
#   All rights reserved.
#   BSD license.
import random
from networkx.utils import *
__all__ = ["approx_clustering_coefficient"]
__author__ = """Fred Morstatter (fred.morstatter@asu.edu)"""

@not_implemented_for('directed')
def approx_clustering_coefficient(G, num_trials=1000):
    r"""Approximation of the clustering coefficient

    Find an approximate clustering coefficient for the graph.

    Parameters
    ----------
    G : NetworkX graph

    num_trials : Number of trials to perform (default 1000). Must be a positive integer.

    Returns
    -------
    Approximated clustering coefficient - float.

    References
    ----------
    .. [1] Schank, Thomas, and Dorothea Wagner. Approximating clustering-coefficient and transitivity. Universität Karlsruhe, Fakultät für Informatik, 2004.
       http://www.emis.ams.org/journals/JGAA/accepted/2005/SchankWagner2005.9.2.pdf
    """
    
    if num_trials <= 0:
        raise ValueError("Expected positive integer for num_trials.")

    #number of successful trials
    triangles_found = 0
    nodes = G.nodes()

    for trial in xrange(num_trials):
        #randomly select a node
        node = random.choice(nodes)
        nbrs = G[node]
        #if there are fewer than 2 connections, this experiment will surely fail, and it's fine to continue as this does say something about the graph.
        if len(nbrs) < 2:
            continue
        else:
            #make a legitimate attempt at the experiment. Choose two of the nodes connections and see if they are connected
            (a, b) = random.sample(nbrs, 2)
            triangles_found += 1 if b in G[a] else 0

    #the clustering coefficient is then the number of triangles found / the number of trials
    return triangles_found / float(num_trials)


