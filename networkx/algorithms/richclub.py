# -*- coding: utf-8 -*-
import networkx as nx
__author__ = """\n""".join(['Ben Edwards',
                            'Aric Hagberg <hagberg@lanl.gov>'])

__all__ = ['rich_club_coefficient']

def rich_club_coefficient(G, normalized=True, Q=100):
    """Return the rich-club coefficient of the graph G.

    The rich-club coefficient is the ratio, for every degree k, of the
    number of actual to the number of potential edges for nodes 
    with degree greater than k: 

    .. math::

        \\phi(k) = \\frac{2 Ek}{Nk(Nk-1)}

    where Nk is the number of nodes with degree larger than k, and Ek
    be the number of edges among those nodes.

    Parameters
    ----------
    G : NetworkX graph 
    normalized : bool (optional)
       Normalize using randomized network (see [1]_)
    Q : float (optional, default=100)
       If normalized=True build a random network by performing 
       Q*M double-edge swaps, where M is the number of edges in G,
       to use as a null-model for normalization.

    Returns
    -------       
    rc : dictionary 
       A dictionary, keyed by degree, with rich club coefficient values.

    Examples
    --------
    >>> G = nx.Graph([(0,1),(0,2),(1,2),(1,3),(1,4),(4,5)])
    >>> rc = nx.rich_club_coefficient(G,normalized=False)
    >>> rc[0] # doctest: +SKIP 
    0.4

    Notes
    ------
    The rich club definition and algorithm are found in [1]_.  This
    algorithm ignores any edge weights and is not defined for directed
    graphs or graphs with parallel edges or self loops.

    Estimates for appropriate values of Q are found in [2]_.

    References
    ----------
    .. [1] Julian J. McAuley, Luciano da Fontoura Costa, and Tibério S. Caetano,
       "The rich-club phenomenon across complex network hierarchies",
       Applied Physics Letters Vol 91 Issue 8, August 2007.
       http://arxiv.org/abs/physics/0701290
    .. [2] R. Milo, N. Kashtan, S. Itzkovitz, M. E. J. Newman, U. Alon,
       "Uniform generation of random graphs with arbitrary degree 
       sequences", 2006. http://arxiv.org/abs/cond-mat/0312028
    """
    if G.is_multigraph() or G.is_directed():
        raise Exception('rich_club_coefficient is not implemented for ',
                        'directed or multiedge graphs.')
    if len(G.selfloop_edges()) > 0:
        raise Exception('rich_club_coefficient is not implemented for ',
                        'graphs with self loops.')
    rc=_compute_rc(G)
    if normalized:
        # make R a copy of G, randomize with Q*|E| double edge swaps
        # and use rich_club coefficient of R to normalize
        R = G.copy()
        E = R.number_of_edges()
        nx.double_edge_swap(R,Q*E,max_tries=Q*E*10)
        rcran=_compute_rc(R)
        for d in rc:
#            if rcran[d] > 0:
            rc[d]/=rcran[d]
    return rc


def _compute_rc(G):
    # compute rich club coefficient for all k degrees in G
    deghist = nx.degree_histogram(G)
    total = sum(deghist)
    # number of nodes with degree > k (omit last entry which is zero)
    nks = [total-cs for cs in nx.utils.cumulative_sum(deghist) if total-cs > 1]
    deg=G.degree()
    edge_degrees=sorted(sorted((deg[u],deg[v])) for u,v in G.edges_iter()) 
    ek=G.number_of_edges()
    k1,k2=edge_degrees.pop(0)
    rc={}
    for d,nk in zip(range(len(nks)),nks):         
        while k1 <= d:
            if len(edge_degrees)==0:
                break
            k1,k2=edge_degrees.pop(0)
            ek-=1
        rc[d] = 2.0*ek/(nk*(nk-1))
    return rc

