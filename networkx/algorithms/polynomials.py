"""Provides algorithms supporting the computation of graph polynomials.

Graph polynomials are polynomial-valued graph invariants that encode a wide
variety of structural information. Examples include the Tutte polynomial,
chromatic polynomial, characteristic polynomial, and matching polynomial. An
extensive treatment is provided in [1]_.

.. [1] Y. Shi, M. Dehmer, X. Li, I. Gutman,
   "Graph Polynomials"
"""
from collections import deque
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["tutte_polynomial"]


@not_implemented_for("directed")
def tutte_polynomial(G):
    r"""Compute a graph's Tutte polynomial via an iterative version of the
    deletion-contraction algorithm.

    The Tutte polynomial `T_G(x, y)` is a fundamental graph polynomial invariant in
    two variables. It encodes a wide array of information related to the
    edge-connectivity of a graph; "Many problems about graphs can be reduced to
    problems of finding and evaluating the Tutte polynomial at certain values" [1]_.
    In fact, every deletion-contraction-expressible feature of a graph is a
    specialization of the Tutte polynomial [2]_ (see Notes for examples).

    There are several equivalent definitions; here are three:

    Def 1 (rank-nullity expansion): For `G` an undirected graph, `n(G)` the
    number of vertices of `G`, `E` the edge set of `G`, and `c(A)`` the number of
    connected components of `A` [3]_:

    .. math::

        T_G(x, y) = \sum_{A \in E} (x-1)^{c(A) - c(G)} (y-1)^{c(A) + |A| - n(G)}

    Def 2 (spanning tree expansion): For `G` an undirected graph, `T` a spanning
    tree of `G`, `i(T)` the internal activity of `T`, and `e(T)` the external
    activity of `T` [4]_:

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
    Some specializations of the Tutte polynomial:
    - `T_G(1, 1)` counts the number of spanning trees of `G`
    - `T_G(1, 2)` counts the number of connected spanning subgraphs of `G`
    - `T_G(2, 1)` counts the number of spanning forests in `G`
    - `T_G(0, 2)` counts the number of strong orientations of `G`
    - `T_G(2, 0)` counts the number of acyclic orientations of `G`

    Edge contraction is defined and deletion-contraction is introduced in [5]_.
    Combinatorial meaning of the coefficients is introduced in [6]_.
    Universality, properties, and applications are discussed in [7]_.

    Practically, up-front computation of the Tutte polynomial may be useful when
    users wish to repeatedly calculate edge-connectivity-related information
    about one or more graphs.

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
    .. [3] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 14
    .. [4] Y. Shi, M. Dehmer, X. Li, I. Gutman,
       "Graph Polynomials," p. 46
    .. [5] D. B. West,
       "Introduction to Graph Theory," p. 84
    .. [6] G. Coutinho,
       "A brief introduction to the Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://homepages.dcc.ufmg.br/~gabriel/seminars/coutinho_tuttepolynomial_seminar.pdf
    .. [7] J. A. Ellis-Monaghan, C. Merino,
       "Graph polynomials and their applications I: The Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://arxiv.org/pdf/0803.3079.pdf
    """
    import sympy

    x = sympy.Symbol("x")
    y = sympy.Symbol("y")
    stack = deque()
    stack.append(nx.MultiGraph(G))

    polynomial = 0
    while stack:
        G = stack.pop()
        bridges = nx.cut_edges(G)
        loops = list(nx.selfloop_edges(G, keys=True))
        edges_not_cuts_loops = [
            i for i in G.edges if i not in bridges and i not in loops
        ]
        if not edges_not_cuts_loops:
            polynomial += x ** len(bridges) * y ** len(loops)
        else:
            e = edges_not_cuts_loops[0]
            # deletion-contraction
            C = nx.contracted_edge(G, e, self_loops=True)
            C.remove_edge(*(e[0], e[0]))
            G.remove_edge(*e)
            stack.append(G)
            stack.append(C)
    return sympy.simplify(polynomial)
