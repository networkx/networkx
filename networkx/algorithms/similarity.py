# Copyright 2015 Janu Verma <j.verma5@gmail.com> and NetworkX developers.
# All rights reserved.
# BSD License.
"""Functions that compute the similarity of nodes in a graph."""
from __future__ import division

from itertools import product

__all__ = ['simrank_similarity']


def _is_close(d1, d2, atolerance=0, rtolerance=0):
    # Pre-condition: d1 and d2 have the same keys at each level if they
    # are dictionaries.
    if not isinstance(d1, dict) and not isinstance(d2, dict):
        return abs(d1 - d2) <= atolerance + rtolerance * abs(d2)
    return all(all(_is_close(d1[u][v], d2[u][v]) for v in d1[u]) for u in d1)


def simrank_similarity(G, source=None, target=None, importance_factor=0.9,
                       max_iterations=100, tolerance=1e-4):
    """Returns the SimRank similarity of nodes in the graph ``G``.

    The SimRank algorithm for determining node similarity is defined in
    [1]_.

    Parameters
    ----------
    G : NetworkX graph
        A NetworkX graph

    source : node
        If this is specified, the returned dictionary maps each node
        ``v`` in the graph to the similarity between ``source`` and
        ``v``.

    target : node
        If both ``source`` and ``target`` are specified, the similarity
        value between ``source`` and ``target`` is returned. If
        ``target`` is specified but ``source`` is not, this argument is
        ignored.

    importance_factor : float
        The relative importance of indirect neighbors with respect to
        direct neighbors.

    max_iterations : integer
        Maximum number of iterations.

    tolerance : float
        Error tolerance used to check convergence. When an iteration of
        the algorithm finds that no similarity value changes more than
        this amount, the algorithm halts.

    Returns
    -------
    similarity : dictionary or float
        If ``source`` and ``target`` are both ``None``, this returns a
        dictionary of dictionaries, where keys are node pairs and value
        are similarity of the pair of nodes.

        If ``source`` is not ``None`` but ``target`` is, this returns a
        dictionary mapping node to the similarity of ``source`` and that
        node.

        If neither ``source`` nor ``target`` is ``None``, this returns
        the similarity value for the given pair of nodes.

    Examples
    --------
    If the nodes of the graph are numbered from zero to *n*, where *n*
    is the number of nodes in the graph, you can create a SimRank matrix
    from the return value of this function where the node numbers are
    the row and column indices of the matrix::

        >>> import networkx as nx
        >>> from numpy import array
        >>> G = nx.cycle_graph(4)
        >>> sim = nx.simrank_similarity(G)
        >>> array([[sim[u][v] for v in sorted(sim[u])] for u in sorted(sim)])

    References
    ----------
    .. [1] G. Jeh and J. Widom.
           "SimRank: a measure of structural-context similarity",
           In KDD'02: Proceedings of the Eighth ACM SIGKDD
           International Conference on Knowledge Discovery and Data Mining,
           pp. 538--543. ACM Press, 2002.
    """
    # This is the definition from the paper:
    #
    # def simrank(G, u, v):
    #     in_neighbors_u = G.predecessors(u)
    #     in_neighbors_v = G.predecessors(v)
    #     scale = C / len(in_neighbors_u) * len(in_neighbors_v)
    #     return scale * sum(simrank(G, w, x)
    #                        for w, x in product(in_neighbors_u,
    #                                            in_neighbors_v))
    #
    prevsim = None
    newsim = {u: {v: 1 if u == v else 0 for v in G} for u in G}
    # These functions compute the update to the similarity value of the nodes
    # `u` and `v` with respect to the previous similarity values.
    avg_sim = lambda s: sum(newsim[w][x] for (w, x) in s) / len(s)
    sim = lambda u, v: importance_factor * avg_sim(list(product(G[u], G[v])))
    for i in range(max_iterations):
        if prevsim and _is_close(prevsim, newsim, tolerance):
            break
        prevsim = newsim
        newsim = {u: {v: sim(u, v) if u is not v else 1
                      for v in newsim[u]} for u in newsim}
    if source is not None and target is not None:
        return newsim[source][target]
    if source is not None:
        return newsim[source]
    return newsim
