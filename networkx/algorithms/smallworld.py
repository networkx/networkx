#    Copyright (C) 2017 by
#    Romain Fontugne <romain@iij.ad.jp>
#    All rights reserved.
#    BSD license.
"""Functions for estimating the small-world-ness of graphs.  
A small world network is characterized by a small average shortest path length, 
and a large clustering coefficient.
Small-worldness is commonly measured with the coefficient sigma or omega. Both
coefficients compare the average clustering coefficient and shortest path 
length of a given graph against the same quantities for an equivalent random
or lattice graph; for more information,
see the Wikipedia article on small-world network [1]_.

.. [1] Small-world network:: https://en.wikipedia.org/wiki/Small-world_network 

"""
import networkx as nx
from networkx.utils import *
import random 
__author__ = """Romain Fontugne (romain@iij.ad.jp)"""
__all__ = ['random_reference','lattice_reference','sigma', 'omega']


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def random_reference(G, niter=10):
    """Compute a random graph by rewiring edges of the given graph while 
    keeping the same degree distribution.


    Parameters
    ----------
    G : graph
       An undirected graph

    niter : integer (optional, default=1)
       An edge is rewired approximatively niter times.

    Returns
    -------
    G : graph
       The randomized graph.

    Notes
    -----
    Does not enforce any connectivity constraints.

    The implementation is adapted from the algorithm by Maslov and Sneppen 
    (2002) [1]_.

    References
    ----------
    .. [1] Maslov, Sergei, and Kim Sneppen. "Specificity and stability in 
    topology of protein networks." Science 296.5569 (2002): 910-913.

    """
    if G.is_directed():
        raise nx.NetworkXError(\
            "random_reference() not defined for directed graphs.")
    if len(G) < 4:
        raise nx.NetworkXError("Graph has less than four nodes.")

    G = G.copy()
    keys,degrees = zip(*G.degree()) # keys, degree
    cdf=nx.utils.cumulative_distribution(degrees)  # cdf of degree
    nnodes = len(G)
    nedges = nx.number_of_edges(G)
    niter = niter*nedges
    ntries = int(nnodes*nedges/(nnodes*(nnodes-1)/2))
    swapcount = 0

    for i in range(niter):
        n=0
        while n < ntries:
            # pick two random edges without creating edge list
            # choose source node indices from discrete distribution
            (ai,ci)=nx.utils.discrete_sequence(2,cdistribution=cdf)
            if ai==ci:
                continue # same source, skip
            a=keys[ai] # convert index to label
            c=keys[ci]
            # choose target uniformly from neighbors
            b = random.choice(list(G.neighbors(a)))
            d = random.choice(list(G.neighbors(c)))
            bi = keys.index(b)
            di = keys.index(d)
            if b in [a,c,d] or d in [a,b,c]:
                continue # all vertices should be different

            if (d not in G[a]) and (b not in G[c]): # don't create parallel edges
                G.add_edge(a,d)
                G.add_edge(c,b)
                G.remove_edge(a,b)
                G.remove_edge(c,d)
                swapcount+=1
                break
            n+=1
    return G

@not_implemented_for('directed')
@not_implemented_for('multigraph')
def lattice_reference(G, niter=10, D=None): 
    """Latticize the given graph by rewiring edges while keeping the same 
    degree distribution.


    Parameters
    ----------
    G : graph
       An undirected graph

    niter : integer (optional, default=1)
       An edge is rewired approximatively niter times.

    D: numpy.array (optional, default=None)
       Distance to the diagonal matrix. 

    Returns
    -------
    G : graph
       The randomized graph.

    Notes
    -----
    Does not enforce any connectivity constraints.

    The implementation is adapted from the algorithm by Sporns et al. which is
    inspired from the original work from Maslov and Sneppen (2002) [2]_.

    References
    ----------
    .. [1] Sporns, Olaf, and Jonathan D. Zwi. "The small world of the cerebral 
    cortex." Neuroinformatics 2.2 (2004): 145-162.
    .. [2] Maslov, Sergei, and Kim Sneppen. "Specificity and stability in 
    topology of protein networks." Science 296.5569 (2002): 910-913.

    """
    import numpy as np

    if G.is_directed():
        raise nx.NetworkXError(\
            "lattice_reference() not defined for directed graphs.")
    if len(G) < 4:
        raise nx.NetworkXError("Graph has less than four nodes.")
    # Instead of choosing uniformly at random from a generated edge list,
    # this algorithm chooses nonuniformly from the set of nodes with
    # probability weighted by degree.
    G = G.copy()
    keys,degrees = zip(*G.degree()) # keys, degree
    cdf=nx.utils.cumulative_distribution(degrees)  # cdf of degree

    nnodes = len(G)
    nedges = nx.number_of_edges(G)
    if D is None:
        D = np.zeros((nnodes, nnodes))
        un = np.arange(1, nnodes)
        um = np.arange(nnodes - 1, 0, -1)
        u = np.append((0,), np.where(un < um, un, um))

        for v in range(int(np.ceil(nnodes / 2))):
            D[nnodes - v - 1, :] = np.append(u[v + 1:], u[:v + 1])
            D[v, :] = D[nnodes - v - 1, :][::-1]
    
    niter = niter*nedges
    ntries = int(nnodes*nedges/(nnodes*(nnodes-1)/2))
    swapcount = 0

    for i in range(niter):
        n=0
        while n < ntries:
            # pick two random edges without creating edge list
            # choose source node indices from discrete distribution
            (ui,xi)=nx.utils.discrete_sequence(2,cdistribution=cdf)
            if ui==xi:
                continue # same source, skip
            u=keys[ui] # convert index to label
            x=keys[xi]
            # choose target uniformly from neighbors
            v = random.choice(list(G.neighbors(u)))
            y = random.choice(list(G.neighbors(x)))
            vi = keys.index(v)
            yi = keys.index(y)
            # if random.random() < 0.5: 
                # ui,u,vi,v = vi,v,ui,u
            if v==y or v==u or v==x or y==u or y==x:
                continue # all vertices should be different

            if (x not in G[u]) and (y not in G[v]): # don't create parallel edges
                if D[ui, vi] + D[xi, yi] >= D[ui, xi] + D[vi, yi]: 
                    # only swap if we get
                    # closer to the diagonal
                    G.add_edge(u,x)
                    G.add_edge(v,y)
                    G.remove_edge(u,v)
                    G.remove_edge(x,y)
                    swapcount+=1
                    break
            n+=1

    return G



@not_implemented_for('directed')
@not_implemented_for('multigraph')
def sigma(G, niter=100, nrand=10):
    """Return the small-world coefficient (sigma) of the given graph.

    The small-world coefficient is defined as:
    sigma = C/Cr / L/Lr
    where C and L are respectively the average clustering coefficient and 
    average shortest path length of G. Cr and Lr are respectively the average 
    clustering coefficient and average shortest path length of an equivalent 
    random graph.

    A graph is commonly classified as small-world if sigma>1.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    niter: integer (optional, default=100)
        Approximate number of rewiring per edge to compute the equivalent 
        random graph.

    nrand: integer (optional, default=10)
        Number of random graphs generated to compute the average clustering
        coefficient (Cr) and average shortest path length (Lr).

    Returns
    -------
    sigma
        The small-world coefficient of G.

    Notes
    -----
    The implementation is adapted from the algorithm by Humphries et al. 
    [1]_[2]_.


    References
    ----------
    .. [1] The brainstem reticular formation is a small-world, not scale-free, 
    network M. D. Humphries, K. Gurney and T. J. Prescott, Proc. Roy. Soc. B 
    2006 273, 503–511, doi:10.1098/rspb.2005.3354
    .. [2] Humphries and Gurney (2008). "Network 'Small-World-Ness': A 
    Quantitative Method for Determining Canonical Network Equivalence". PLoS 
    One. 3 (4). PMID 18446219. doi:10.1371/journal.pone.0002051.

    """
    import numpy as np

    # Compute the mean clustering coefficient and average shortest path length
    # for an equivalent random graph
    randMetrics = {"C":[], "L": []}
    for i in range(nrand):
        Gr = random_reference(G, niter=niter)
        randMetrics["C"].append(nx.algorithms.average_clustering(Gr))
        randMetrics["L"].append(nx.algorithms.average_shortest_path_length(Gr))

    C = nx.algorithms.average_clustering(G)
    L = nx.algorithms.average_shortest_path_length(G)
    Cr = np.mean(randMetrics["C"])
    Lr = np.mean(randMetrics["L"])

    sigma = (C/Cr)/(L/Lr)

    return sigma


@not_implemented_for('directed')
@not_implemented_for('multigraph')
def omega(G, niter=100, nrand=10):
    """Return the small-world coefficient (omega) of the given graph, which is:
    
    omega = Lr/L - C/Cl
    
    where C and L are respectively the average clustering coefficient and 
    average shortest path length of G. Lr is the average shortest path length 
    of an equivalent random graph and Cl is the average clustering coefficient
    of an equivalent lattice graph.

    The small-world coefficient (omega) ranges between -1 and 1. Values close
    to 0 means the G features small-world characteristics. Values close to -1
    means G has a lattice shape whereas values close to 1 means G is a random 
    graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    niter: integer (optional, default=100)
        Approximate number of rewiring per edge to compute the equivalent 
        random graph.

    nrand: integer (optional, default=10)
        Number of random graphs generated to compute the average clustering
        coefficient (Cr) and average shortest path length (Lr).

    Returns
    -------
    omega 
        The small-work coefficient (omega)

    Notes
    -----
    The implementation is adapted from the algorithm by Telesford et al. [1]_.

    References
    ----------
    .. [1] Telesford, Joyce, Hayasaka, Burdette, and Laurienti (2011). "The 
    Ubiquity of Small-World Networks". Brain Connectivity. 1 (0038): 367–75. 
    PMC 3604768. PMID 22432451. doi:10.1089/brain.2011.0038.
    """

    # Compute the mean clustering coefficient and average shortest path length
    # for an equivalent random graph
    randMetrics = {"C":[], "L": []}
    for i in range(nrand):
        Gr = random_reference(G, niter=niter)
        Gl = lattice_reference(G, niter=niter)
        randMetrics["C"].append(nx.algorithms.average_clustering(Gl))
        randMetrics["L"].append(nx.algorithms.average_shortest_path_length(Gr))

    C = nx.algorithms.average_clustering(G)
    L = nx.algorithms.average_shortest_path_length(G)
    Cl = np.mean(randMetrics["C"])
    Lr = np.mean(randMetrics["L"])

    omega = (Lr/L) - (C/Cl)

    return omega

# fixture for nose tests
def setup_module(module):
    from nose import SkipTest
    try:
        import numpy
    except:
        raise SkipTest("NumPy not available")
