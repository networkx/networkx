# See https://github.com/networkx/networkx/pull/1474
# Copyright 2011 Reya Group <http://www.reyagroup.com>
# Copyright 2011 Alex Levenson <alex@isnotinvain.com>
# Copyright 2011 Diederik van Liere <diederik.vanliere@rotman.utoronto.ca>
"""Functions for analyzing triads of a graph."""

from networkx.utils import not_implemented_for
from itertools import combinations, permutations
from collections import defaultdict

__all__ = __all__ = ['triadic_census', 'all_triplets', 'all_triads',
                     'triads_by_type', 'triad_type', 'random_triad',
                     'triadic_closures', 'focal_closures', 'balanced_triads']

#: The integer codes representing each type of triad.
#:
#: Triads that are the same up to symmetry have the same code.
TRICODES = (1, 2, 2, 3, 2, 4, 6, 8, 2, 6, 5, 7, 3, 8, 7, 11, 2, 6, 4, 8, 5, 9,
            9, 13, 6, 10, 9, 14, 7, 14, 12, 15, 2, 5, 6, 7, 6, 9, 10, 14, 4, 9,
            9, 12, 8, 13, 14, 15, 3, 7, 8, 11, 7, 12, 14, 15, 8, 14, 13, 15,
            11, 15, 15, 16)

#: The names of each type of triad. The order of the elements is
#: important: it corresponds to the tricodes given in :data:`TRICODES`.
TRIAD_NAMES = ('003', '012', '102', '021D', '021U', '021C', '111D', '111U',
               '030T', '030C', '201', '120D', '120U', '120C', '210', '300')


#: A dictionary mapping triad code to triad name.
TRICODE_TO_NAME = {i: TRIAD_NAMES[code - 1] for i, code in enumerate(TRICODES)}


def _tricode(G, v, u, w):
    """Returns the integer code of the given triad.

    This is some fancy magic that comes from Batagelj and Mrvar's paper. It
    treats each edge joining a pair of `v`, `u`, and `w` as a bit in
    the binary representation of an integer.

    """
    combos = ((v, u, 1), (u, v, 2), (v, w, 4), (w, v, 8), (u, w, 16),
              (w, u, 32))
    return sum(x for u, v, x in combos if v in G[u])


@not_implemented_for('undirected')
def triadic_census(G):
    """Determines the triadic census of a directed graph.

    The triadic census is a count of how many of the 16 possible types of
    triads are present in a directed graph.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    census : dict
       Dictionary with triad type as keys and number of occurrences as values.

    Notes
    -----
    This algorithm has complexity $O(m)$ where $m$ is the number of edges in
    the graph.

    See also
    --------
    triad_graph

    References
    ----------
    .. [1] Vladimir Batagelj and Andrej Mrvar, A subquadratic triad census
        algorithm for large sparse networks with small maximum degree,
        University of Ljubljana,
        http://vlado.fmf.uni-lj.si/pub/networks/doc/triads/triads.pdf

    """
    # Initialize the count for each triad to be zero.
    census = {name: 0 for name in TRIAD_NAMES}
    n = len(G)
    # m = dict(zip(G, range(n)))
    m = {v: i for i, v in enumerate(G)}
    for v in G:
        vnbrs = set(G.pred[v]) | set(G.succ[v])
        for u in vnbrs:
            if m[u] <= m[v]:
                continue
            neighbors = (vnbrs | set(G.succ[u]) | set(G.pred[u])) - {u, v}
            # Calculate dyadic triads instead of counting them.
            if v in G[u] and u in G[v]:
                census['102'] += n - len(neighbors) - 2
            else:
                census['012'] += n - len(neighbors) - 2
            # Count connected triads.
            for w in neighbors:
                if m[u] < m[w] or (m[v] < m[w] < m[u] and
                                   v not in G.pred[w] and
                                   v not in G.succ[w]):
                    code = _tricode(G, v, u, w)
                    census[TRICODE_TO_NAME[code]] += 1
    # null triads = total number of possible triads - all found triads
    #
    # Use integer division here, since we know this formula guarantees an
    # integral value.
    census['003'] = ((n * (n - 1) * (n - 2)) // 6) - sum(census.values())
    return census


@not_implemented_for('undirected')
def all_triplets(G):
    """Returns a generator of all possible sets of 3 nodes in a DiGraph.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    triplets : generator of 3-tuples
       Generator of tuples of 3 nodes
    """
    triplets = combinations(G.nodes(), 3)
    return triplets


@not_implemented_for('undirected')
def all_triads(G):
    """A generator of all possible triads in G.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    all_triads : generator of DiGraphs
       Generator of triads (order-3 DiGraphs)
    """
    triplets = combinations(G.nodes(), 3)
    for triplet in triplets:
        yield G.subgraph(triplet).copy()


@not_implemented_for('undirected')
def triads_by_type(G):
    """Returns a list of all triads for each triad type in a directed graph.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    tri_by_type : dict
       Dictionary with triad types as keys and lists of triads as values.
    """
    o = G.order()
    assert o >= 3, "G should have at least 3 nodes."
    # num_triads = o * (o - 1) * (o - 2) // 6
    # if num_triads > TRIAD_LIMIT: print(WARNING)
    all_tri = all_triads(G)
    tri_by_type = defaultdict(list)
    for triad in all_tri:
        name = triad_type(triad)
        tri_by_type[name].append(triad)
    return tri_by_type


@not_implemented_for('undirected')
def triad_type(G):
    """Returns the sociological triad type for a triad.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph with 3 nodes

    Returns
    -------
    triad_type : str
       A string identifying the triad type
    """
    assert G.order() == 3, 'Graph is not a triad'
    num_edges = len(G.edges())
    if num_edges == 6:
        return "300"
    elif num_edges == 5:
        return "210"
    elif num_edges == 0:
        return "003"
    elif num_edges == 1:
        return "012"
    elif num_edges == 2:
        e1, e2 = G.edges()
        if set(e1) == set(e2):
            return "102"
        elif e1[0] == e2[0]:
            return "021D"
        elif e1[1] == e2[1]:
            return "021U"
        elif e1[1] == e2[0] or e2[1] == e1[0]:
            return "021C"
    elif num_edges == 3:
        for (e1, e2, e3) in permutations(G.edges(), 3):
            if set(e1) == set(e2):
                if e3[0] in e1:
                    return "111U"
                if e3[1] in e1:
                    return "111D"
            elif set(e1).symmetric_difference(set(e2)) == set(e3):
                if {e1[0], e2[0], e3[0]} == {e1[0], e2[0],
                                             e3[0]} == set(G.nodes()):
                    return "030C"
                if e3 == (e1[0], e2[1]) and e2 == (e1[1], e3[1]):
                    return "030T"
    elif num_edges == 4:
        for (e1, e2, e3, e4) in permutations(G.edges(), 4):
            if set(e1) == set(e2):
                if set(e3) == set(e4):
                    return "201"
                if {e3[0]} == {e4[0]} == set(e3).intersection(set(e4)):
                    return "120D"
                if {e3[1]} == {e4[1]} == set(e3).intersection(set(e4)):
                    return "120U"
                if e3[1] == e4[0]:
                    return "120C"
    else:
        raise ValueError("Invalid triad G")


@not_implemented_for('undirected')
def random_triad(G):
    """Returns a random triad from a directed graph.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    G2 : subgraph
       A randomly selected triad (order-3 NetworkX DiGraph)
    """
    pass


@not_implemented_for('undirected')
def triadic_closures(G):
    """Returns a list of order-3 subgraphs of G that are triadic closures.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph

    Returns
    -------
    closures : list
       List of triads of G that are triadic closures
    """
    pass


@not_implemented_for('undirected')
def focal_closures(G, attr_name):
    """Returns a list of order-3 subgraphs of G that are focally closed.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph
    attr_name : str
        An attribute name


    Returns
    -------
    closures : list
       List of triads of G that are focally closed on attr_name
    """
    pass


@not_implemented_for('undirected')
def balanced_triads(G, crit_func):
    """Returns a list of order-3 subgraphs of G that are stable.

    Parameters
    ----------
    G : digraph
       A NetworkX DiGraph
    crit_func : function
       A function that determines if a triad (order-3 digraph) is stable

    Returns
    -------
    triads : list
       List of triads in G that are stable
    """
    pass
