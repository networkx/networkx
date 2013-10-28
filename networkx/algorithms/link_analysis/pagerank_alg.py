"""PageRank analysis of graph structure. """
#    Copyright (C) 2004-2011 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
#    NetworkX:http://networkx.lanl.gov/
import networkx as nx
from networkx.exception import NetworkXError
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__all__ = ['pagerank', 'pagerank_numpy', 'pagerank_scipy', 'google_matrix']


def pagerank(G, alpha=0.85, personalization=None,
             max_iter=100, tol=1.0e-8, nstart=None, weight='weight',
             dangling_edges=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.

    Parameters
    -----------
    G : graph
      A NetworkX graph.

    alpha : float, optional
      Damping parameter for PageRank, default=0.85.

    personalization: dict, optional
      The "personalization vector" consisting of a dictionary with a
      key for every graph node and nonzero personalization value for each node.

    max_iter : integer, optional
      Maximum number of iterations in power method eigenvalue solver.

    tol : float, optional
      Error tolerance used to check convergence in power method solver.

    nstart : dictionary, optional
      Starting value of PageRank iteration for each node.

    weight : key, optional
      Edge data key to use as weight.  If None weights are set to 1.

    dangling_edges: dict, optional
      The outedges to be assigned to any "dangling" nodes, i.e., nodes without
      any outedges. The dict key is the node the outedge points to and the dict
      value is the weight of that outedge. By default, dangling nodes will be
      given outedges to all other nodes in the graph with uniform weight. This
      must be selected to result in an irreducible transition matrix (see notes
      under google_matrix). It may be common to have the dangling_edges dict to
      be the same as the personalization dict.

    Returns
    -------
    pagerank : dictionary
       Dictionary of nodes with PageRank as value

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(4))
    >>> pr = nx.pagerank(G, alpha=0.9)

    Notes
    -----
    The eigenvector calculation is done by the power iteration method
    and has no guarantee of convergence.  The iteration will stop
    after max_iter iterations or an error tolerance of
    number_of_nodes(G)*tol has been reached.

    The PageRank algorithm was designed for directed graphs but this
    algorithm does not check if the input graph is directed and will
    execute on undirected graphs by converting each oriented edge in the
    directed graph to two edges.

    See Also
    --------
    pagerank_numpy, pagerank_scipy, google_matrix

    References
    ----------
    .. [1] A. Langville and C. Meyer,
       "A survey of eigenvector methods of web information retrieval."
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry,
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    if isinstance(G, nx.MultiGraph) or isinstance(G, nx.MultiDiGraph):
        raise Exception("pagerank() not defined for graphs with multiedges.")

    if len(G) == 0:
        return {}

    if not G.is_directed():
        D = G.to_directed()
    else:
        D = G

    # create a copy in (right) stochastic form
    W = nx.stochastic_graph(D, weight=weight)
    N = W.number_of_nodes()

    # choose fixed starting vector if not given
    if nstart is None:
        x = dict.fromkeys(W, 1.0 / N)
    else:
        # Normalized nstart vector
        s = float(sum(nstart.values()))
        x = {k: v / s for k, v in nstart.items()}

    # assign uniform personalization/teleportation vector if not given
    if personalization is None:
        p = dict.fromkeys(W, 1.0 / N)
    else:
        s = float(sum(personalization.values()))
        p = {k: v / s for k, v in personalization.items()}
        if set(p) != set(G):
            raise NetworkXError('Personalization vector '
                                'must have a value for every node')

    # "dangling" nodes, no links out from them
    dangling_nodes = [n for n in W if W.out_degree(n) == 0.0]
    if dangling_edges:
        dangling_weights = dict.fromkeys(W, 0)
        s = float(sum(dangling_edges.values()))
        for n, w in dangling_edges.items():
            if n not in W:
                raise NetworkXError(
                    'The node %s does not exist in the graph' % str(n))
            dangling_weights[n] = w / s
    else:
        dangling_weights = dict.fromkeys(W, 1.0 / N)

    i = 0
    while True:  # power iteration: make up to max_iter iterations
        xlast = x
        x = dict.fromkeys(xlast.keys(), 0)
        danglesum = alpha * sum(xlast[n] for n in dangling_nodes)
        for n in x:
            # this matrix multiply looks odd because it is
            # doing a left multiply x^T=xlast^T*W
            for nbr in W[n]:
                x[nbr] += alpha * xlast[n] * W[n][nbr][weight]
            x[n] += danglesum * dangling_weights[n] + (1.0 - alpha) * p[n]
        # check convergence, l1 norm
        err = sum([abs(x[n] - xlast[n]) for n in x])
        if err < tol:
            break
        if i > max_iter:
            raise NetworkXError('pagerank: power iteration failed to converge '
                                'in %d iterations.' % (i - 1))
        i += 1
    return x


def google_matrix(G, alpha=0.85, personalization=None,
                  nodelist=None, weight='weight', dangling_edges=None):
    """Return the Google matrix of the graph.

    Parameters
    -----------
    G : graph
      A NetworkX graph.

    alpha : float
      The damping factor.

    personalization: dict, optional
      The "personalization vector" consisting of a dictionary with a
      key for every graph node and nonzero personalization value for each node.

    nodelist : list, optional
      The rows and columns are ordered according to the nodes in nodelist.
      If nodelist is None, then the ordering is produced by G.nodes().

    weight : key, optional
      Edge data key to use as weight.  If None weights are set to 1.

    dangling_edges: dict, optional
      The outedges to be assigned to any "dangling" nodes, i.e., nodes without
      any outedges. The dict key is the node the outedge points to and the dict
      value is the weight of that outedge. By default, dangling nodes will be
      given outedges to all other nodes in the graph with uniform weight. This
      must be selected to result in an irreducible transition matrix (see notes
      below). It may be common to have the dangling_edges dict to be the same as
      the personalization dict.

    Returns
    -------
    A : NumPy matrix
       Google matrix of the graph

    Notes
    -----
    The matrix returned represents the transition matrix that describes the
    Markov chain used in PageRank. For PageRank to converge to a unique
    solution (i.e., a unique stationary distribution in a Markov chain), the
    transition matrix must be irreducible. In other words, it must be that there
    exists a path between every pair of nodes in the graph, or else there is the
    potential of "rank sinks."

    See Also
    --------
    pagerank, pagerank_numpy, pagerank_scipy
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("google_matrix() requires NumPy: http://scipy.org/")

    # choose ordering in matrix
    if personalization is None:  # use G.nodes() ordering
        nodelist = G.nodes()
    else:  # use personalization "vector" ordering
        nodelist = personalization.keys()
        if set(nodelist) != set(G):
            raise NetworkXError('Personalization vector dictionary '
                                'must have a value for every node')

    M = nx.to_numpy_matrix(G, nodelist=nodelist, weight=weight)
    (n, m) = M.shape  # should be square
    if n == 0:
        return M

    # We need to convert the dangling_edges dictionary into an array with
    # indices that match `nodelist`.
    if dangling_edges:
        dangling_edge_array = np.repeat(0, n)
        for node, weight in dangling_edges.items():
            if node not in nodelist:
                raise NetworkXError(
                    'The node %s does not exist in the graph' % str(node))
            dangling_edge_array[nodelist.index(node)] = weight
    else:
        dangling_edge_array = np.ones(n)

    # Treat any dangling nodes, if any
    dangling_nodes = np.where(M.sum(axis=1) == 0)[0]
    for node in dangling_nodes:
        M[node] = dangling_edge_array

    M /= M.sum(axis=1)  # Normalize so that entries in each row equal to 1
    # add "teleportation"/personalization
    if personalization:
        v = np.array(list(personalization.values()), dtype=float)
    else:
        v = np.ones(n)
    v /= v.sum()
    P = alpha * M + (1 - alpha) * np.outer(np.ones(n), v)
    return P


def pagerank_numpy(G, alpha=0.85, personalization=None, weight='weight',
                   dangling_edges=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.

    Parameters
    -----------
    G : graph
      A NetworkX graph.

    alpha : float, optional
      Damping parameter for PageRank, default=0.85.

    personalization: dict, optional
       The "personalization vector" consisting of a dictionary with a
       key for every graph node and nonzero personalization value for each node.

    weight : key, optional
      Edge data key to use as weight.  If None weights are set to 1.

    dangling_edges: dict, optional
      The outedges to be assigned to any "dangling" nodes, i.e., nodes without
      any outedges. The dict key is the node the outedge points to and the dict
      value is the weight of that outedge. By default, dangling nodes will be
      given outedges to all other nodes in the graph with uniform weight. This
      must be selected to result in an irreducible transition matrix (see notes
      under google_matrix). It may be common to have the dangling_edges dict to
      be the same as the personalization dict.

    Returns
    -------
    pagerank : dictionary
       Dictionary of nodes with PageRank as value.

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(4))
    >>> pr = nx.pagerank_numpy(G, alpha=0.9)

    Notes
    -----
    The eigenvector calculation uses NumPy's interface to the LAPACK
    eigenvalue solvers.  This will be the fastest and most accurate
    for small graphs.

    This implementation works with Multi(Di)Graphs.

    See Also
    --------
    pagerank, pagerank_scipy, google_matrix

    References
    ----------
    .. [1] A. Langville and C. Meyer,
       "A survey of eigenvector methods of web information retrieval."
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry,
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    try:
        import numpy as np
    except ImportError:
        raise ImportError("pagerank_numpy() requires NumPy: http://scipy.org/")
    if len(G) == 0:
        return {}
    # choose ordering in matrix
    if personalization is None:  # use G.nodes() ordering
        nodelist = G.nodes()
    else:  # use personalization "vector" ordering
        nodelist = personalization.keys()
    M = google_matrix(G, alpha, personalization=personalization,
                      nodelist=nodelist, weight=weight,
                      dangling_edges=dangling_edges)
    # use numpy LAPACK solver
    eigenvalues, eigenvectors = np.linalg.eig(M.T)
    ind = eigenvalues.argsort()
    # eigenvector of largest eigenvalue at ind[-1], normalized
    largest = np.array(eigenvectors[:, ind[-1]]).flatten().real
    norm = float(largest.sum())
    centrality = dict(zip(nodelist, map(float, largest / norm)))
    return centrality


def pagerank_scipy(G, alpha=0.85, personalization=None,
                   max_iter=100, tol=1.0e-6, weight='weight',
                   dangling_edges=None):
    """Return the PageRank of the nodes in the graph.

    PageRank computes a ranking of the nodes in the graph G based on
    the structure of the incoming links. It was originally designed as
    an algorithm to rank web pages.

    Parameters
    -----------
    G : graph
      A NetworkX graph.

    alpha : float, optional
      Damping parameter for PageRank, default=0.85.

    personalization: dict, optional
       The "personalization vector" consisting of a dictionary with a
       key for every graph node and nonzero personalization value for each node.

    max_iter : integer, optional
      Maximum number of iterations in power method eigenvalue solver.

    tol : float, optional
      Error tolerance used to check convergence in power method solver.

    weight : key, optional
      Edge data key to use as weight.  If None weights are set to 1.

    dangling_edges: dict, optional
      The outedges to be assigned to any "dangling" nodes, i.e., nodes without
      any outedges. The dict key is the node the outedge points to and the dict
      value is the weight of that outedge. By default, dangling nodes will be
      given outedges to all other nodes in the graph with uniform weight. This
      must be selected to result in an irreducible transition matrix (see notes
      under google_matrix). It may be common to have the dangling_edges dict to
      be the same as the personalization dict.

    Returns
    -------
    pagerank : dictionary
       Dictionary of nodes with PageRank as value

    Examples
    --------
    >>> G = nx.DiGraph(nx.path_graph(4))
    >>> pr = nx.pagerank_scipy(G, alpha=0.9)

    Notes
    -----
    The eigenvector calculation uses power iteration with a SciPy
    sparse matrix representation.

    See Also
    --------
    pagerank, pagerank_numpy, google_matrix

    References
    ----------
    .. [1] A. Langville and C. Meyer,
       "A survey of eigenvector methods of web information retrieval."
       http://citeseer.ist.psu.edu/713792.html
    .. [2] Page, Lawrence; Brin, Sergey; Motwani, Rajeev and Winograd, Terry,
       The PageRank citation ranking: Bringing order to the Web. 1999
       http://dbpubs.stanford.edu:8090/pub/showDoc.Fulltext?lang=en&doc=1999-66&format=pdf
    """
    try:
        import scipy.sparse
    except ImportError:
        raise ImportError("pagerank_scipy() requires SciPy: http://scipy.org/")

    if len(G) == 0:
        return {}

    # choose ordering in matrix
    if personalization is None:  # use G.nodes() ordering
        nodelist = G.nodes()
    else:  # use personalization "vector" ordering
        nodelist = personalization.keys()

    M = nx.to_scipy_sparse_matrix(
        G, nodelist=nodelist, weight=weight, dtype='f')
    (n, m) = M.shape  # should be square
    S = scipy.array(M.sum(axis=1)).flatten()
    S[S > 0] = 1.0 / S[S > 0]
    Q = scipy.sparse.spdiags(S.T, 0, *M.shape, format='csr')
    M = Q * M
    x = scipy.repeat(1.0 / n, n)  # initial vector

    # Set up the outgoing edge weights for dangling nodes
    if dangling_edges:
        dangle_weights = scipy.repeat(0.0, n)
        s = float(sum(dangling_edges.values()))
        for node, weight in dangling_edges.items():
            if node not in nodelist:
                raise NetworkXError(
                    'The node %s does not exist in the graph' % str(node))
            dangle_weights[nodelist.index(node)] = weight / s
    else:
        dangle_weights = scipy.repeat(1.0 / n, n)
    dangles, _ = scipy.where(M.sum(axis=1) == 0)  # the nodes that are dangling

    # add "teleportation"/personalization
    if personalization is not None:
        v = scipy.array(list(personalization.values()), dtype=float)
        v = v / v.sum()
    else:
        v = scipy.repeat(1.0 / n, n)

    # power iteration: make up to max_iter iterations
    i = 0
    while i <= max_iter:
        xlast = x
        x = alpha * (x * M + sum(x[dangles]) * dangle_weights) + \
                (1 - alpha) * v
        # check convergence, l1 norm
        err = scipy.absolute(x - xlast).sum()
        if err < n * tol:
            return dict(zip(nodelist, map(float, x)))
        i += 1
    raise NetworkXError('pagerank_scipy: power iteration failed to converge '
                        'in %d iterations.' % (i + 1))


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
