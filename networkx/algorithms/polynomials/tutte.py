"""Functions supporting the computation of the Tutte polynomial of a graph.

The Tutte polynomial $T_G(x, y)$ is a fundamental graph polynomial invariant in
two variables. It encodes a wide array of information related to the
edge-connectivity of a graph; "Many problems about graphs can be reduced to
problems of finding and evaluating the Tutte polynomial at certain values" [1]_.
For instance, at $y=0$, the Tutte polynomial retrieves the chromatic polynomial.
Some more specializations:
- $T_G(1, 1)$ counts the number of spanning trees of $G$
- $T_G(1, 2)$ counts the number of connected spanning subgraphs of $G$
- $T_G(2, 1)$ counts the number of spanning forests in $G$
- $T_G(0, 2)$ counts the number of strong orientations of $G$
- $T_G(2, 0)$ counts the number of acyclic orientations of $G$

Practically, up-front computation of the Tutte polynomial may be useful when
users wish to repeatedly calculate edge-connectivity-related information about
one or more graphs. A general treatment of the Tutte polynomial is provided in
[2]_.

References
----------
.. [1] M. Brandt,
   "The Tutte Polynomial."
   Talking About Combinatorial Objects Seminar, 2015
   https://math.berkeley.edu/~brandtm/talks/tutte.pdf
.. [2] Wikipedia,
   "Tutte polynomial"
   https://en.wikipedia.org/wiki/Tutte_polynomial#Chromatic_polynomial
"""
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["tutte_polynomial"]


@not_implemented_for("directed")
def tutte_polynomial(G, simplify=True):
    r"""Compute a graph's Tutte polynomial via deletion-contraction.

    The Tutte polynomial `T_G(x, y)` is a fundamental graph polynomial invariant
    in two variables, encoding a wide array of information related to the
    edge-connectivity of a graph. There are several equivalent definitions; here
    are three:

    Def 1 (rank-nullity expansion): For `G` an undirected graph, `n(G)` the
    number of vertices of `G`, `E` the edge set of `G`, and `c(A)`` the number of
    connected components of `A` [1]_:

    .. math::

        T_G(x, y) = \sum_{A \in E} (x-1)^{c(A) - c(G)} (y-1)^{c(A) + |A| - n(G)}

    Def 2 (spanning tree expansion): For `G` an undirected graph, `T` a spanning
    tree of `G`, `i(T)` the internal activity of `T`, and `e(T)` the external
    activity of `T` [2]_:

    .. math::

        T_G(x, y) = \sum_{T \text{ a spanning tree of } G} x^{i(T)} y^{e(T)}

    Def 3 (deletion-contraction recurrence): For `G` an undirected graph, `G-e`
    the graph obtained from `G` by deleting edge `e`, `G/e` the graph obtained
    from `G` by contracting edge `e`, `k(G)` the number of cut-edges of `G`,
    and `l(G)` the number of loops of `G`:

    .. math::
        T_G(x, y) = \begin{cases}
    	   x^{k(G)} y^{l(G)}, & \text{if all edges of $G$ are cut-edges or loops} \\
           T_{G-e}(x, y) + T_{G/e}(x, y), & \text{otherwise, for $e$ not a cut-edge or loop}
        \end{cases}

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
    x**4 + 6*x**3 + 10*x**2*y + 11*x**2 + 5*x*y**3 + 15*x*y**2 + 20*x*y + 6*x + y**6 + 4*y**5 + 10*y**4 + 15*y**3 + 15*y**2 + 6*y

    Notes
    -----
    This function implements the deletion-contraction recurrence (Definition 3,
    described above). Edge contraction is defined and deletion-contraction is
    introduced in [3]_. Combinatorial meaning of the coefficients is introduced
    in [4]_. Universality, properties, and applications are discussed in [5]_.

    See Also
    --------
    _get_cut_edges

    References
    ----------
    .. [1] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 14
    .. [2] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 46
    .. [3] D. B. West,
       "Introduction to Graph Theory," p. 84
    .. [4] G. Coutinho,
       "A brief introduction to the Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://homepages.dcc.ufmg.br/~gabriel/seminars/coutinho_tuttepolynomial_seminar.pdf
    .. [5] J. A. Ellis-Monaghan, C. Merino,
       "Graph polynomials and their applications I: The Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://arxiv.org/pdf/0803.3079.pdf
    """
    import sympy

    G = nx.MultiGraph(G)

    components = list(nx.connected_components(G))
    if len(components) > 1:
        t = 1
        for component in components:
            t *= tutte_polynomial(G.subgraph(component), False)
        return sympy.simplify(t)

    cut_edges = _get_cut_edges(G)
    loops = [e for e in G.edges if e[0] == e[1]]
    edges_not_cuts_loops = [i for i in G.edges if i not in cut_edges and i not in loops]

    if not edges_not_cuts_loops:
        return sympy.Symbol("x") ** len(cut_edges) * sympy.Symbol("y") ** len(loops)

    e = edges_not_cuts_loops[0]
    # deletion-contraction
    C = nx.contracted_edge(G, e, self_loops=True)
    contraction_loops = [i for i in C.edges if i[0] == i[1] and i not in G.edges]
    if contraction_loops:
        C.remove_edge(*contraction_loops[0])
    G.remove_edge(*e)

    t = tutte_polynomial(G, False) + tutte_polynomial(C, False)
    if simplify:
        return sympy.simplify(t)
    return t


def _get_cut_edges(G):
    """Finds the cut-edges of a provided graph.

    Cut-edges are edges whose deletion increases the number of components of a
    graph [1]_. A cut-edge is an edge that is not a member of any cycle.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    list
        A list of all cut-edges of `G`.

    References
    ----------
    .. [1] D. B. West,
       "Introduction to Graph Theory," p. 23
    """
    cut_edges = []
    for e in G.edges:
        G_copy = G.copy()
        G_copy.remove_edge(*e)
        if len(list(nx.connected_components(G_copy))) > 1:
            cut_edges.append(e)
    return cut_edges
