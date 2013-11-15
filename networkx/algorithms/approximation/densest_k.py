"""Densest k subgraph problem is to find the maximum density subgraph on
exactly k vertices. This problem is known to be NP-Hard by a reduction
from the clique problem.
"""

import random
import warnings
import networkx as nx
from networkx.utils.decorators import not_implemented_for

#TODO: given a node, find densest_k_subgraph containing this node.
#TODO: densest subgraph problem is not included in NetworkX yet?


@not_implemented_for('directed')
def densest_k_nodes(G, k):
    """Return the list of nodes in G with the highest density among them.

    This is not optimum solution, but a polynomial approximate algorithm. The
    performance bound is proven in the referred papers.

    Returns
    -------
    k_nodes : list
        list of nodes

    Examples
    --------
    >>> G = nx.house_graph()
    >>> import networkx.algorithms.approximation as apxa
    >>> apxa.densest_k_nodes(G, 3)
    >>> [2, 3, 4]

    See Also
    --------
    densest_k_subgraph

    Notes
    -----

    References
    ----------
    [1] U. Feige, G. Kortsarz, and D. Peleg. The dense k-subgraph problem.
    Algorithmica, 29(3):410-421.

    [2] Doron Goldstein, Michael Langberg. The Dense k Subgraph problem. CoRR.
    2009
    """
    return algorithm_A(G, k)


@not_implemented_for('directed')
def densest_k_subgraph(G, k, copy=True):
    """

    Returns
    -------
    D : NetworkX Graph
        undirected graph

    Examples
    --------
    >>> G = nx.house_graph()
    >>> import networkx.algorithms.approximation as apxa
    >>> apxa.densest_k_subgraph(G, 3).nodes()
    >>> [2, 3, 4]

    See Also
    --------
    densest_k_nodes

    Notes
    -----

    References
    ----------
    [1] U. Feige, G. Kortsarz, and D. Peleg. The dense k-subgraph problem.
    Algorithmica, 29(3):410-421.

    [2] Doron Goldstein, Michael Langberg. The Dense k Subgraph problem. CoRR.
    2009
    """
    k_nodes = densest_k_nodes(G, k)
    if copy:
        return G.subgraph(k_nodes).copy()
    else:
        return G.subgraph(k_nodes)


@not_implemented_for('directed')
def densest_k_nodes_brute_force(G, k):
    """Return the densest set of k nodes in G

    Returns
    -------
    k_nodes : list
        list of nodes

    Examples
    --------
    >>> G = nx.house_graph()
    >>> import networkx.algorithms.approximation as apxa
    >>> apxa.densest_k_nodes_brute_force(G, 3)
    >>> [2, 3, 4]

    See Also
    --------
    densest_k_subgraph_brute_force
    """
    import itertools
    k_nodes = []
    max_density = 0.
    comb_iter = itertools.combinations(G.nodes_iter(), k)
    for comb in comb_iter:
        density = __density(G, comb)
        if max_density < density:
            k_nodes = comb
            max_density = density

    # TODO: what happens when no such subgraph is founded (in which case the
    # above for loop would be passed). I just return k_nodes(=[]) here.

    return list(k_nodes)


@not_implemented_for('directed')
def densest_k_subgraph_brute_force(G, k, copy=True):
    """Return the densest subgroup of G with k nodes

    Returns
    -------
    k_nodes : list
        list of nodes

    D : NetworkX Graph
        undirected graph

    Examples
    --------
    >>> G = nx.house_graph()
    >>> import networkx.algorithms.approximation as apxa
    >>> apxa.densest_k_subgraph_brute_force(G, 3).nodes()
    >>> [2, 3, 4]

    See Also
    --------
    densest_k_nodes_brute_force
    """
    k_nodes = densest_k_nodes_brute_force(G, k)
    if copy:
        return G.subgraph(k_nodes).copy()
    else:
        return G.subgraph(k_nodes)


@not_implemented_for('directed')
def __trivial(G, k):
    """A trival random selection

    Select k/2 arbitrary edges from G. Return the set of vertices incident
    with these edges, adding arbitrary vertices to this set if its size is
    smaller than k.

    Returns a set of nodes.

    Notes
    ----
    As proven in the paper [1], This algorithm guarantee result density >= 1.

    If no such set of nodes is founded, return [].
    """
    if k > len(G):
        return []
    try:
        rand_edges = random.sample(G.edges(), k/2)
        rand_nodes = set(__[0] for __ in rand_edges)
        rand_nodes.update(set(__[1] for __ in rand_edges))
    except ValueError:
        rand_nodes = random.sample(G.nodes(), k)
    while len(rand_nodes) < k:
        rand_nodes.add(random.choice(G.nodes()))

    return list(rand_nodes)


@not_implemented_for('directed')
def __greedy(G, k):
    """A greedy procedure

    Sort the vertices by order of their degree. Let H denote the k/2 vertices
    with highest degrees in G (breaking ties arbitrarily). Sort the remaining
    vertices by the number of neighbors they have in H. Let C denote the k/2
    vertices in G\H with the largest number of neighbors in H . Return H | C .

    Notes
    ----
    As proven in the paper [1], This algorithm guarantee result density >=
    k*d_H / (2*n), where d_H denote average degree of k/2 vertices with highest
    degrees in G.

    If no such set of nodes is founded, return [].
    """
    if k > len(G):
        return []
    nodes_by_degree = sorted(
        G.nodes(), key=lambda x: G.degree(x), reverse=True)
    H = nodes_by_degree[:k-k/2]
    setH = set(H)

    cmpf = lambda x: len(set(G.neighbors(x)) & setH)
    nodes_by_H = sorted(nodes_by_degree[k-k/2:], key=cmpf, reverse=True)
    C = nodes_by_H[:k/2]

    selected_nodes = setH | set(C)

    return list(selected_nodes)


@not_implemented_for('directed')
def __walks2(G, k):
    """Procedure using walks of length 2

    For vertices v,w and integer l >= 1, Wl(v,w) denotes the number of walks of
    length l from v to w.  Compute W2(u, v) for all pairs of vertices.
    Construct a candidate graph Hv for every vertex v in G, as follows: Sort
    the vertices of G by nonincreasing order of their number of length-2 walks
    to v, W2(v, w1) >= W2(v, w2) >= ... Let Phv denote the set {w1,...,
    wk/2}.  Compute for every neighbor x of v the number of edges connecting x
    to Phv, deg(x, Phv), and construct a set Bv containing the k/2 neighbors of
    v with highest deg(x, Phv). Let Hv denote the subgraph induced on Phv | Bv.
    (If Hv still contains less than k vertices, then it is completed to size k
    arbitrarily.) Select the densest candidate graph Hv as the output.

    Notes
    ----
    If no such set of nodes is founded, return [].

    As proven in the paper [1], This algorithm guarantee result density >=
    (d*)^2 / (2*max(k, 2*\deltaG)), where d* denote average degree of the
    optimum solution, and \deltaG is the highest degree of vertices in G.
    """
    if k > len(G):
        return []
    W_l = number_of_walks_batch(G, 2)
    Hv = set()
    max_density = 0.
    for v in G.nodes_iter():
        nodes_by_wl = sorted(G.nodes(), key=lambda x: W_l[v][x], reverse=True)
        Phv = nodes_by_wl[:k-k/2]
        setPhv = set(Phv)

        cmpf = lambda x: len(set(G.neighbors(x)) & setPhv)
        nodes_by_Phv = sorted(G.neighbors(v), key=cmpf, reverse=True)
        Bv = nodes_by_Phv[:k/2]

        candidates = set(Bv) | setPhv

        while len(candidates) < k:
            # random pick to complement finial result set
            # XXX: This makes algorithm not stable
            candidates.add(random.choice(G.nodes()))

        density = __density(G, candidates)
        if (max_density < density):
            max_density = density
            Hv = candidates

    return list(Hv)


@not_implemented_for('directed')
def algorithm_A(G, k):
    """Algorithm A employs three different procedures (1:trival, 2:greedy, and
    3:walks2) to select a dense subgraph, and returns the densest of the three
    subgraphs that are found.

    Procedures 1 and 2 are applied to the original input graph G. Procedure 3
    however is applied to the graph Gl induced on the vertices of V\H, where H
    is the set of k/2 vertices of highest degree in G, as defined in procedure
    2.

    Notes
    -----
    As proven in the paper [1], This algorithm has the approximation ratio of
    O(n^\frac{-1}{3}). More precisely, A(G, k) >= \frac{d*(G,
    k)}{2*n^\frac{1}{3}}, where d*(G, k) is the optimum solution's average
    degree.

    If no such set of nodes is founded, return [].
    """
    nodes_by_degree = sorted(
        G.nodes(), key=lambda x: G.degree(x), reverse=True)
    # __walks2() are applied on G_l induced on V\H, where H is the set of k/2
    # vertices with highest degree in original G.
    G_l = G.subgraph(nodes_by_degree[k/2+1:])
    candidates = [__trivial(G, k), __greedy(G, k), __walks2(G_l, k)]
    densities = [__density(G, __) for __ in candidates]
    return candidates[densities.index(max(densities))]


# @not_implemented_for('directed')
# def __walks3(G, k):
#     """Procedure 4 as in the paper [1]
#     1. For all pairs ofvertices vi,vj \in G_l,apply algorithm_A(N(vi)|N(vj),
#     k).
#     2. Return the densest of the subgraph returned by any of the O(n^2)
#     applications of algorithm_A.
#     """
#     max_density = 0.
#     k_nodes = []
#     for i in G.nodes_iter():
#         for j in G.nodes_iter():
#             sub_G = G.subgraph(G.neighbors(i) + G.neighbors(j))
#             candidates = algorithm_A(sub_G, k)
#             density = __density(G, candidates)
#         if (max_density < density):
#             max_density = density
#             k_nodes = candidates
#
#     return k_nodes
#
#
# @not_implemented_for('directed')
# def __walks5():
#     pass
#
#
# @not_implemented_for('directed')
# def algorithm_B(G, k):
#     candidates = [__walks3(G, k), __walks5(G, k)]
#     densities = [__density(G, __) for __ in candidates]
#     return candidates[densities.index(max(densities))]


@not_implemented_for('directed')
def __density(G, nodes):
    """The density defined in the paper I referred to, dG of a graph G = G(V,
    E) is its average degree. That is, dG = 2|E|/|V|. For undirected graph, it
    is just average degree.

    Notes
    -----
    This is different from networkx's density() funciton definition. I used the
    definition in the paper.
    """
    # I added this function because it diverges from NetworkX's density()
    # function. Waiting for peer review here: how we measure density.

#    # it is unnecessary to make a whole subgraph just to calculate the density
#    sub_G = G.subgraph(nodes)
#    return 2*sub_G.number_of_edges()/sub_G.number_of_nodes()

    if nodes:
        return (2.*sum(1 for __ in G.edges_iter(nodes) if __[1] in nodes)
                / len(nodes))
    else:
        return 0


def number_of_walks(G, source, target, length):
    """
    A walk of length l is a sequence of l + 1 vertices in which consecutive
    vertices are adjacent (hence the walk follows l edges). The vertices of a
    walk need not be distinct.

    Returns the number of walks of length l that start at vertex source and end
    at vertex target.
    """
    last = [source]  # last visited nodes
    for __ in range(0, length):
        last = [neighbor for node in last for neighbor in G.neighbors(node)]

    return sum([1 for node in last if node == target])


def number_of_walks_batch(G, length, sparse=True):
    """
    Parameters
    ----------
    sparse: bool
        True if to use scipy sparse matrix, otherwise numpy dense matrix

    A walk of length l is a sequence of l + 1 vertices in which consecutive
    vertices are adjacent (hence the walk follows l edges). The vertices of a
    walk need not be distinct.

    Matrix multiplication (raising the adjacency matrix of the graph to the lth
    power) can be used in order to compute Wl(vi , vj ) for all pairs of
    vertices simultaneously.

    Returns dictionary[i][j] : number_of_walks from node i to j
    """
    if sparse:
        # I'm guessing using numpy is more common, so if scipy not available,
        # silently default to numpy dense matrix here.
        try:
            import scipy
        except ImportError:
            sparse = False
            warnings.warn("Python module scipy is not available, using numpy \
                           dense matrix instead.", ImportWarning)
    if sparse:
        adj_matrix = nx.to_scipy_sparse_matrix(G, dtype=int, weight=None)
    else:
        adj_matrix = nx.to_numpy_matrix(G, dtype=int, weight=None)

    adj_matrix **= length
    # just need to make the result independent of numpy lib, besides, networkx
    # may have nodes other than integers.
    W_l = {}
    for i, nd_i in enumerate(G.nodes_iter()):
        for j, nd_j in enumerate(G.nodes_iter()):
            W_l.setdefault(nd_i, {}).setdefault(nd_j, adj_matrix[i, j])

    return W_l
