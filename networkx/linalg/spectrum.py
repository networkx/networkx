"""
Eigenvalue spectrum of graphs.
"""
#    Copyright (C) 2004-2013 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import networkx as nx
__author__ = "\n".join(['Aric Hagberg <aric.hagberg@gmail.com>',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult(dschult@colgate.edu)'])

__all__ = ['laplacian_spectrum', 'adjacency_spectrum']


def laplacian_spectrum(G, weight='weight'):
    """Return eigenvalues of the Laplacian of G

    Parameters
    ----------
    G : graph
       A NetworkX graph

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    laplacian_matrix
    """
    from scipy.linalg import eigvalsh
    return eigvalsh(nx.laplacian_matrix(G, weight=weight).todense())


def adjacency_spectrum(G, weight='weight'):
    """Return eigenvalues of the adjacency matrix of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph

    weight : string or None, optional (default='weight')
       The edge data key used to compute each value in the matrix.
       If None, then each edge has weight 1.

    Returns
    -------
    evals : NumPy array
      Eigenvalues

    Notes
    -----
    For MultiGraph/MultiDiGraph, the edges weights are summed.
    See to_numpy_matrix for other options.

    See Also
    --------
    adjacency_matrix
    """
    from scipy.linalg import eigvals
    return eigvals(nx.adjacency_matrix(G, weight=weight).todense())

# fixture for nose tests


def setup_module(module):
    from nose import SkipTest
    try:
        import scipy.linalg
    except:
        raise SkipTest("scipy.linalg not available")
