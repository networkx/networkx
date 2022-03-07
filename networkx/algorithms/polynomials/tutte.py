"""Functions supporting the computation of the Tutte polynomial of a graph.

The Tutte polynomial `T_G(x, y)` is a fundamental graph polynomial invariant in
two variables. It encodes a wide array of information related to the
edge-connectivity of a graph; "Many problems about graphs can be reduced to
problems of finding and evaluating the Tutte polynomial at certain values" [1]_.
In fact, every deletion-contraction-expressible feature of a graph is a
specialization of the Tutte polynomial [2]_.

For instance, at `y=0`, the Tutte polynomial retrieves the chromatic polynomial.
Some more specializations:
- `T_G(1, 1)` counts the number of spanning trees of `G`
- `T_G(1, 2)` counts the number of connected spanning subgraphs of `G`
- `T_G(2, 1)` counts the number of spanning forests in `G`
- `T_G(0, 2)` counts the number of strong orientations of `G`
- `T_G(2, 0)` counts the number of acyclic orientations of `G`

Practically, up-front computation of the Tutte polynomial may be useful when
users wish to repeatedly calculate edge-connectivity-related information about
one or more graphs. A general treatment of the Tutte polynomial is provided in
[3]_.

References
----------
.. [1] M. Brandt,
   "The Tutte Polynomial."
   Talking About Combinatorial Objects Seminar, 2015
   https://math.berkeley.edu/~brandtm/talks/tutte.pdf
.. [2] A. Björklund, T. Husfeldt, P. Kaski, M. Koivisto,
   "Computing the Tutte polynomial in vertex-exponential time"
   49th Annual IEEE Symposium on Foundations of Computer Science, 2008
   https://ieeexplore.ieee.org/abstract/document/4691000
.. [3] Wikipedia,
   "Tutte polynomial"
   https://en.wikipedia.org/wiki/Tutte_polynomial#Chromatic_polynomial
"""
from itertools import chain, combinations
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["tutte_polynomial", "tutte_polynomial_recursive"]


@not_implemented_for("directed")
def tutte_polynomial_recursive(G, simplify=True):
    r"""Compute a graph's Tutte polynomial via the classical
    deletion-contraction algorithm.

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
    	   x^{k(G)} y^{l(G)}, & \text{if all edges are cut-edges or loops} \\
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
    >>> nx.tutte_polynomial_recursive(C)
    x**4 + x**3 + x**2 + x + y

    >>> D = nx.diamond_graph()
    >>> nx.tutte_polynomial_recursive(D)
    x**3 + 2*x**2 + 2*x*y + x + y**2 + y

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
            t *= tutte_polynomial_recursive(G.subgraph(component), False)
        return sympy.simplify(t)

    cut_edges = nx.cut_edges(G)
    loops = list(nx.selfloop_edges(G, keys=True))
    edges_not_cuts_loops = [i for i in G.edges if i not in cut_edges and i not in loops]

    if not edges_not_cuts_loops:
        return sympy.Symbol("x") ** len(cut_edges) * sympy.Symbol("y") ** len(loops)

    e = edges_not_cuts_loops[0]
    # deletion-contraction
    C = nx.contracted_edge(G, e, self_loops=True)
    C.remove_edge(*(e[0], e[0]))
    G.remove_edge(*e)

    t = tutte_polynomial_recursive(G, False) + tutte_polynomial_recursive(C, False)
    if simplify:
        return sympy.simplify(t)
    return t


def _partition_sum(G):
    r"""Calculates a partition sum from the q-state Potts model via induced
    subgraphs.

    Def: For `G` an undirected graph with vertex set `V` and edge set `E`, and
    `c(F)` the number of connected components of the graph with vertex set `V`
    and edge set `F`, we calculate:

    .. math::

        Z_G(q, v) = \sum_{F \subseteq E} q^{c(F)} v^{|F|}

    Parameters
    ----------
    G : NetworkX Graph

    Notes
    -----
    The Potts model is introduced in [1]_. A survey of the Potts model partition
    function and its relation to the Tutte polynomial can be found in [2]_. The
    partition sum used here is a specialization of equation 1.1.

    References
    ----------
    .. [1] R. B. Potts,
       "Some generalized order-disorder transformations"
       Mathematical Proceedings of the Cambridge Philosophical Society, 1952
       https://doi.org/10.1017/S0305004100027419
    .. [2] A. Sokal,
       "The multivariate Tutte polynomial (alias Potts model) for graphs and matroids"
       20th British Combinatorial Conference, 2005
       https://arxiv.org/abs/math/0503607
    """
    import sympy

    q = sympy.Symbol("q")
    v = sympy.Symbol("v")
    edges = list(G.edges)
    result = 0
    # iterate over all unique subsets of the edge set
    for f in chain.from_iterable(combinations(edges, r) for r in range(len(edges) + 1)):
        F = nx.Graph()
        F.add_nodes_from(G)
        F.add_edges_from(f)
        k = nx.number_connected_components(F)
        if k != 0:
            result += (q ** k) * (v ** len(f))
    return result


@not_implemented_for("directed")
def tutte_polynomial(G):
    r"""Compute a graph's Tutte polynomial via the partition sum of the q-state
    Potts model.

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
    	   x^{k(G)} y^{l(G)}, & \text{if all edges are cut-edges or loops} \\
           T_{G-e}(x, y) + T_{G/e}(x, y), & \text{otherwise, for $e$ not a cut-edge or loop}
        \end{cases}

    Parameters
    ----------
    G : NetworkX Graph

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

    Notes
    -----
    This function obtains the Tutte polynomial by a transformation of its
    multivariate form (equations 4 and 5 in [3]_). Edge contraction is defined
    and deletion-contraction is introduced in [4]_. Combinatorial meaning of the
    coefficients is introduced in [5]_. Universality, properties, and
    applications are discussed in [6]_.

    See Also
    --------
    tutte_polynomial_recursive

    References
    ----------
    .. [1] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 14
    .. [2] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 46
    .. [3] A. Björklund, T. Husfeldt, P. Kaski, M. Koivisto,
       "Computing the Tutte polynomial in vertex-exponential time"
       49th Annual IEEE Symposium on Foundations of Computer Science, 2008
       https://ieeexplore.ieee.org/abstract/document/4691000
    .. [4] D. B. West,
       "Introduction to Graph Theory," p. 84
    .. [5] G. Coutinho,
       "A brief introduction to the Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://homepages.dcc.ufmg.br/~gabriel/seminars/coutinho_tuttepolynomial_seminar.pdf
    .. [6] J. A. Ellis-Monaghan, C. Merino,
       "Graph polynomials and their applications I: The Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://arxiv.org/pdf/0803.3079.pdf
    """
    import sympy

    if len(G) == 1:
        return 1
    q = sympy.Symbol("q")
    v = sympy.Symbol("v")
    x = sympy.Symbol("x")
    y = sympy.Symbol("y")
    k = nx.number_connected_components(G)
    multivariate_tutte = _partition_sum(G).subs([(q, (x - 1) * (y - 1)), (v, y - 1)])
    tutte = ((x - 1) ** (-k)) * ((y - 1) ** (-len(G))) * multivariate_tutte
    return sympy.simplify(tutte)
