"""Modularity matrix of graphs.
"""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from __future__ import division
import networkx as nx
from networkx.utils import not_implemented_for

__author__ = "\n".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)',
                        'Jean-Gabriel Young <jean.gabriel.young@gmail.com>'])
__all__ = ['modularity_matrix']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def modularity_matrix(G, nodelist=None):
    """Return the modularity matrix of G.

    The modularity matrix is the matrix B = A - <A>, where A is the adjacency
    matrix and <A> is the average adjacency matrix, assuming that the graph
    is descibred by the configuration model.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    nodelist : list, optional
       The rows and columns are ordered according to the nodes in nodelist.
       If nodelist is None, then the ordering is produced by G.nodes().

    Returns
    -------
    B : Numpy matrix
      The modularity matrix of G.

    See Also
    --------
    to_numpy_matrix
    adjacency_matrix
    laplacian_matrix

    References
    ----------
    .. [1] M. E. J. Newman, "Modularity and community structure in networks",
       Proc. Natl. Acad. Sci. USA, vol. 103, pp. 8577-8582, 2006.
    """
    if nodelist is None:
        nodelist = G.nodes()
    A = nx.to_scipy_sparse_matrix(G, nodelist=nodelist, format='csr')
    k = A.sum(axis=1)
    m = G.number_of_edges()
    # Expected adjacency matrix
    X = k * k.transpose() / (2 * m)
    return A - X


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
