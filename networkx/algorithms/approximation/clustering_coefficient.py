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
def approx_clustering_coefficient(G, numTrials=1000):
    r"""Approximation of the clustering coefficient

    Find an approximate clustering coefficient for the graph.

    Parameters
    ----------
    G : NetworkX graph

    numTrials : Number of trials to perform (default 1000).

    Returns
    -------
    Approximated clustering coefficient - float.

    References
    ----------
    .. [1] Schank, Thomas, and Dorothea Wagner. Approximating clustering-coefficient and transitivity. Universität Karlsruhe, Fakultät für Informatik, 2004.
       http://www.emis.ams.org/journals/JGAA/accepted/2005/SchankWagner2005.9.2.pdf
    """
    
    #number of successful trials
    c = 0
    nodes = G.nodes()

    for trial in xrange(numTrials):
        #randomly select a node
        node = random.choice(nodes)
        nodeConnections = G[node].keys()
        #if there are fewer than 2 connections, this experiment will surely fail.
        if len(nodeConnections) < 2:
            continue
        else:
            #make a legitimate attempt at the experiment. Choose two of the nodes connections and see if they are connected
            (a, b) = random.sample(nodeConnections, 2)
            c += 1 if b in set(G[a].keys()) else 0

    #the clustering coefficient is then the number of triangles found / the number of trials
    return float(c) / numTrials


