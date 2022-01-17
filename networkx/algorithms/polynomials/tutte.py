"""Functions supporting the computation of the Tutte polynomial of a graph."""
import sympy
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "tutte_polynomial"
]


@not_implemented_for("directed")
def tutte_polynomial(G, simplify=True):
    """Recursive deletion-contraction algorithm for computing a graph's Tutte
    polynomial.

    Parameters
    ----------
    G : NetworkX graph

    simplify : bool
        determines if the returned expression will be in simplified form

    Returns
    -------
    instance of :class:`sympy.core.add.Add`
        A Sympy expression representing the Tutte polynomial for `G`.

    Examples
    --------
    >>> C = nx.cycle_graph(5)
    >>> nx.tutte_polynomial(C)
    x**4 + x**3 + x**2 + x + y

    >>> D = nx.diamond_graph()
    >>> nx.tutte_polynomial(D)
    x**3 + 2*x**2 + 2*x*y + x + y**2 + y

    >>> K = nx.complete_graph(5)
    >>> nx.tutte_polynomial(K)
    x**4 + 6*x**3 + 10*x**2*y + 11*x**2 + 5*x*y**3 + 15*x*y**2 + 20*x*y + 6*x +
    y**6 + 4*y**5 + 10*y**4 + 15*y**3 + 15*y**2 + 6*y
    """
    G = nx.MultiGraph(G)

    components = list(nx.connected_components(G))
    if len(components) > 1:
        t = 1
        for component in components:
            t *= tutte_polynomial(G.subgraph(component), False)
        return sympy.simplify(t)

    cut_edges = _get_cut_edges(G)
    loops = [e for e in G.edges if e[0] == e[1]]
    edges_not_cuts_loops = [i for i in G.edges
                            if i not in cut_edges and i not in loops]

    if not edges_not_cuts_loops:
        return sympy.Symbol('x')**len(cut_edges) \
            * sympy.Symbol('y')**len(loops)

    e = edges_not_cuts_loops[0]
    # deletion-contraction
    C = nx.contracted_edge(G, e, self_loops=True)
    contraction_loops = [i for i in C.edges
                         if i[0] == i[1] and i not in G.edges]
    if contraction_loops:
        C.remove_edge(*contraction_loops[0])
    G.remove_edge(*e)

    t = tutte_polynomial(G, False) + tutte_polynomial(C, False)
    if simplify:
        return sympy.simplify(t)
    return t


def _get_cut_edges(G):
    """
    Finds the edges whose deletion increases the number of components of a
    graph.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    list
        A list of all cut-edges of `G`.
    """
    cut_edges = []
    for e in G.edges:
        G_copy = G.copy()
        G_copy.remove_edge(*e)
        if len(list(nx.connected_components(G_copy))) > 1:
            cut_edges.append(e)
    return cut_edges
