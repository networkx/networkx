#    Copyright (C) 2017-2019 by
#    Luca Baldesi
#    BSD license.
#
# Author:  Luca Baldesi (luca.baldesi@unitn.it)
"""Generates graphs with a given eigenvector structure"""


import networkx as nx
from networkx.utils import np_random_state

__all__ = ['spectral_graph_forge']


def _truncate(x):
    """ Returns the truncated value of x in the interval [0,1]
    """

    if x < 0:
        return 0
    if x > 1:
        return 1
    return x


def _mat_spect_approx(A, level, sorteigs=True, reverse=False, absolute=True):
    """ Returns the low-rank approximation of the given matrix A

    Parameters
    ----------
    A : numpy matrix
    level : integer
        It represents the fixed rank for the output approximation matrix
    sorteigs : boolean
        Whether eigenvectors should be sorted according to their associated
        eigenvalues before removing the firsts of them
    reverse : boolean
        Whether eigenvectors list should be reversed before removing the firsts
        of them
    absolute : boolean
        Whether eigenvectors should be sorted considering the absolute values
        of the corresponding eigenvalues

    Returns
    -------
    B : numpy matrix
        low-rank approximation of A

    Notes
    -----
    Low-rank matrix approximation is about finding a fixed rank matrix close
    enough to the input one with respect to a given norm (distance).
    In the case of real symmetric input matrix and euclidean distance, the best
    low-rank approximation is given by the sum of first eigenvector matrices.

    References
    ----------
    ..  [1] G. Eckart and G. Young, The approximation of one matrix by another
            of lower rank
    ..  [2] L. Mirsky, Symmetric gauge functions and unitarily invariant norms

    """

    import numpy as np

    d, V = np.linalg.eigh(A)
    d = np.ravel(d)
    n = len(d)
    if sorteigs:
        if absolute:
            k = np.argsort(np.abs(d))
        else:
            k = np.argsort(d)
        # ordered from the lowest to the highest
    else:
        k = range(n)
    if not reverse:
        k = np.flipud(k)

    z = np.zeros((n, 1))
    for i in range(level, n):
        V[:, k[i]] = z

    B = V*np.diag(d)*np.transpose(V)
    return B


@np_random_state(3)
def spectral_graph_forge(G, alpha, transformation='identity', seed=None):
    """Returns a random simple graph with spectrum resembling that of `G`

    This algorithm, called Spectral Graph Forge (SGF), computes the
    eigenvectors of a given graph adjacency matrix, filters them and
    builds a random graph with a similar eigenstructure.
    SGF has been proved to be particularly useful for synthesizing
    realistic social networks and it can also be used to anonymize
    graph sensitive data.

    Parameters
    ----------
    G : Graph
    alpha :  float
        Ratio representing the percentage of eigenvectors of G to consider,
        values in [0,1].
    transformation : string, optional
        Represents the intended matrix linear transformation, possible values
        are 'identity' and 'modularity'
    seed : integer, random_state, or None (default)
        Indicator of numpy random number generation state.
        See :ref:`Randomness<randomness>`.

    Returns
    -------
    H : Graph
        A graph with a similar eigenvector structure of the input one.

    Raises
    ------
    NetworkXError
        If transformation has a value different from 'identity' or 'modularity'

    Notes
    -----
    Spectral Graph Forge (SGF) generates a random simple graph resembling the
    global properties of the given one.
    It leverages the low-rank approximation of the associated adjacency matrix
    driven by the *alpha* precision parameter.
    SGF preserves the number of nodes of the input graph and their ordering.
    This way, nodes of output graphs resemble the properties of the input one
    and attributes can be directly mapped.

    It considers the graph adjacency matrices which can optionally be
    transformed to other symmetric real matrices (currently transformation
    options include *identity* and *modularity*).
    The *modularity* transformation, in the sense of Newman's modularity matrix
    allows the focusing on community structure related properties of the graph.

    SGF applies a low-rank approximation whose fixed rank is computed from the
    ratio *alpha* of the input graph adjacency matrix dimension.
    This step performs a filtering on the input eigenvectors similar to the low
    pass filtering common in telecommunications.

    The filtered values (after truncation) are used as input to a Bernoulli
    sampling for constructing a random adjacency matrix.

    References
    ----------
    ..  [1] L. Baldesi, C. T. Butts, A. Markopoulou, "Spectral Graph Forge:
        Graph Generation Targeting Modularity", IEEE Infocom, '18.
        https://arxiv.org/abs/1801.01715
    ..  [2] M. Newman, "Networks: an introduction", Oxford university press,
        2010

    Examples
    --------
    >>> import networkx as nx
    >>> G = nx.karate_club_graph()
    >>> H = nx.spectral_graph_forge(G, 0.3)
    >>>
    """

    import numpy as np
    import scipy.stats as stats

    available_transformations = ['identity', 'modularity']
    alpha = _truncate(alpha)
    A = nx.to_numpy_matrix(G)
    n = A.shape[1]
    level = int(round(n*alpha))

    if transformation not in available_transformations:
        msg = '\'{0}\' is not a valid transformation. '.format(transformation)
        msg += 'Transformations: {0}'.format(available_transformations)
        raise nx.NetworkXError(msg)

    K = np.ones((1, n)) * A

    B = A
    if (transformation == 'modularity'):
        B -= np.transpose(K) * K / float(sum(np.ravel(K)))

    B = _mat_spect_approx(B, level, sorteigs=True, absolute=True)

    if (transformation == 'modularity'):
        B += np.transpose(K) * K / float(sum(np.ravel(K)))

    B = np.vectorize(_truncate, otypes=[np.float])(B)
    np.fill_diagonal(B, np.zeros((1, n)))

    for i in range(n-1):
        B[i, i+1:] = stats.bernoulli.rvs(B[i, i+1:], random_state=seed)
        B[i+1:, i] = np.transpose(B[i, i+1:])

    H = nx.from_numpy_matrix(B)

    return H


# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
    try:
        import scipy
    except:
        raise SkipTest("SciPy not available")
