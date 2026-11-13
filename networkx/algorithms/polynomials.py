"""Provides algorithms supporting the computation of graph polynomials.

Graph polynomials are polynomial-valued graph invariants that encode a wide
variety of structural information. Examples include the Tutte polynomial,
chromatic polynomial, characteristic polynomial, and matching polynomial. An
extensive treatment is provided in [1]_.

For a simple example, the `~sympy.matrices.matrixbase.MatrixBase.charpoly`
method can be used to compute the characteristic polynomial from the adjacency
matrix of a graph. Consider the complete graph ``K_4``:

>>> import sympy
>>> x = sympy.Symbol("x")
>>> G = nx.complete_graph(4)
>>> A = nx.to_numpy_array(G, dtype=int)
>>> M = sympy.SparseMatrix(A)
>>> M.charpoly(x).as_expr()
x**4 - 6*x**2 - 8*x - 3


.. [1] Y. Shi, M. Dehmer, X. Li, I. Gutman,
   "Graph Polynomials"
"""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ["chromatic_polynomial", "tutte_polynomial"]


def _polynomial_add_term(coefficients, powers, value):
    """Accumulate one exact coefficient, discarding cancellations."""
    coefficient = coefficients.get(powers, 0) + value
    if coefficient:
        coefficients[powers] = coefficient
    else:
        coefficients.pop(powers, None)


def _polynomial_product(left, right):
    """Multiply sparse integer coefficient maps in one or two variables."""
    product = {}
    for left_powers, left_coefficient in left.items():
        for right_powers, right_coefficient in right.items():
            powers = tuple(a + b for a, b in zip(left_powers, right_powers))
            _polynomial_add_term(product, powers, left_coefficient * right_coefficient)
    return product


def _chromatic_block_coefficients(G):
    """Evaluate simple-graph factors with an explicit postorder work stack."""
    from math import comb

    tasks = [("visit", G)]
    results = []
    while tasks:
        operation, value = tasks.pop()
        if operation == "subtract":
            contracted = results.pop()
            deleted = results.pop()
            for powers, coefficient in contracted.items():
                _polynomial_add_term(deleted, powers, -coefficient)
            results.append(deleted)
            continue
        if operation == "product":
            count, components = value
            product = {(components,): 1}
            for _ in range(count):
                block = results.pop()
                # Every edge-containing block is connected and its polynomial
                # is divisible by x. One x remains per connected component.
                reduced = {
                    (degree - 1,): coefficient
                    for (degree,), coefficient in block.items()
                    if degree
                }
                product = _polynomial_product(product, reduced)
            results.append(product)
            continue

        H = value
        n = len(H)
        m = H.number_of_edges()
        components = nx.number_connected_components(H)
        if m == n - components:
            # A forest has x**components * (x - 1)**m.
            results.append(
                {
                    (components + degree,): (-1) ** (m - degree) * comb(m, degree)
                    for degree in range(m + 1)
                }
            )
            continue
        if m == n * (n - 1) // 2:
            # Complete graphs have x * (x - 1) * ... * (x - n + 1).
            complete = {(0,): 1}
            for color in range(n):
                complete = _polynomial_product(complete, {(1,): 1, (0,): -color})
            results.append(complete)
            continue
        if components == 1 and m == n and all(d == 2 for _, d in H.degree):
            # A simple cycle has (x - 1)**n + (-1)**n * (x - 1).
            cycle = {
                (degree,): (-1) ** (n - degree) * comb(n, degree)
                for degree in range(n + 1)
            }
            _polynomial_add_term(cycle, (1,), (-1) ** n)
            _polynomial_add_term(cycle, (0,), -((-1) ** n))
            results.append(cycle)
            continue

        blocks = list(nx.biconnected_components(H))
        if len(blocks) > 1:
            # Reductions can expose articulation points that were not present
            # in the caller's graph. Factor those subproblems as well.
            tasks.append(("product", (len(blocks), components)))
            tasks.extend(("visit", H.subgraph(nodes).copy()) for nodes in blocks)
            continue

        u, v = next(iter(H.edges))
        contracted = nx.contracted_nodes(
            H, u, v, self_loops=False, store_contraction_as=None
        )
        H.remove_edge(u, v)
        tasks.append(("subtract", None))
        tasks.append(("visit", contracted))
        tasks.append(("visit", H))
    return results.pop()


def _tutte_block_coefficients(G):
    """Evaluate multigraph factors with loop/bridge reductions and no recursion."""
    tasks = [("visit", G)]
    results = []
    while tasks:
        operation, value = tasks.pop()
        if operation == "sum":
            x_power, y_power = value
            contracted = results.pop()
            deleted = results.pop()
            for powers, coefficient in contracted.items():
                _polynomial_add_term(deleted, powers, coefficient)
            results.append(
                {
                    (i + x_power, j + y_power): coefficient
                    for (i, j), coefficient in deleted.items()
                }
            )
            continue
        if operation == "product":
            count, x_power, y_power = value
            product = {(x_power, y_power): 1}
            for _ in range(count):
                product = _polynomial_product(product, results.pop())
            results.append(product)
            continue

        H = value
        loops = list(nx.selfloop_edges(H, keys=True))
        H.remove_edges_from(loops)
        y_power = len(loops)
        # One low-link traversal provides both bridges and larger blocks.
        # A two-vertex block is a bridge only when its edge is not parallel.
        x_power = 0
        blocks = []
        for nodes in nx.biconnected_components(H):
            if len(nodes) == 2 and H.number_of_edges(*nodes) == 1:
                x_power += 1
            else:
                blocks.append(nodes)
        if not blocks:
            results.append({(x_power, y_power): 1})
            continue
        if len(blocks) > 1:
            tasks.append(("product", (len(blocks), x_power, y_power)))
            tasks.extend(("visit", H.subgraph(nodes).copy()) for nodes in blocks)
            continue

        if x_power:
            # Bridge factors have already been accumulated. Discard their
            # edges before processing the one remaining nontrivial block.
            H = H.subgraph(blocks[0]).copy()

        # Isolated vertices have Tutte polynomial one. A two-vertex block has
        # only parallel edges: T = x + y + ... + y**(m-1).
        if len(blocks[0]) == 2:
            parallel = {(x_power + 1, y_power): 1}
            parallel.update(
                {
                    (x_power, y_power + degree): 1
                    for degree in range(1, H.number_of_edges())
                }
            )
            results.append(parallel)
            continue

        n = len(blocks[0])
        if H.number_of_edges() == n and all(H.degree[v] == 2 for v in blocks[0]):
            # A simple cycle has T = x**(n-1) + ... + x + y.
            cycle = {(degree + x_power, y_power): 1 for degree in range(1, n)}
            cycle[x_power, y_power + 1] = 1
            results.append(cycle)
            continue

        u, v, key = next(iter(H.edges(keys=True)))
        contracted = nx.contracted_nodes(
            H, u, v, self_loops=True, store_contraction_as=None
        )
        # Exactly one resulting loop represents the selected edge. The other
        # parallel edges become loop factors on the next visit.
        contracted.remove_edge(u, u)
        H.remove_edge(u, v, key)
        tasks.append(("sum", (x_power, y_power)))
        tasks.append(("visit", contracted))
        tasks.append(("visit", H))
    return results.pop()


@not_implemented_for("directed")
@nx._dispatchable
def tutte_polynomial(G):
    r"""Returns the Tutte polynomial of `G`

    This function factors over biconnected blocks and computes each factor
    using iterative deletion-contraction with immediate loop and bridge
    reductions. Intermediate coefficients are exact integers.

    The Tutte polynomial `T_G(x, y)` is a fundamental graph polynomial invariant in
    two variables. It encodes a wide array of information related to the
    edge-connectivity of a graph; "Many problems about graphs can be reduced to
    problems of finding and evaluating the Tutte polynomial at certain values" [1]_.
    In fact, every deletion-contraction-expressible feature of a graph is a
    specialization of the Tutte polynomial [2]_ (see Notes for examples).

    There are several equivalent definitions; here are three:

    Def 1 (rank-nullity expansion): For `G` an undirected graph, `n(G)` the
    number of vertices of `G`, `E` the edge set of `G`, `V` the vertex set of
    `G`, and `c(A)` the number of connected components of the graph with vertex
    set `V` and edge set `A` [3]_:

    .. math::

        T_G(x, y) = \sum_{A \in E} (x-1)^{c(A) - c(E)} (y-1)^{c(A) + |A| - n(G)}

    Def 2 (spanning tree expansion): Let `G` be an undirected graph, `T` a spanning
    tree of `G`, and `E` the edge set of `G`. Let `E` have an arbitrary strict
    linear order `L`. Let `B_e` be the unique minimal nonempty edge cut of
    $E \setminus T \cup {e}$. An edge `e` is internally active with respect to
    `T` and `L` if `e` is the least edge in `B_e` according to the linear order
    `L`. The internal activity of `T` (denoted `i(T)`) is the number of edges
    in $E \setminus T$ that are internally active with respect to `T` and `L`.
    Let `P_e` be the unique path in $T \cup {e}$ whose source and target vertex
    are the same. An edge `e` is externally active with respect to `T` and `L`
    if `e` is the least edge in `P_e` according to the linear order `L`. The
    external activity of `T` (denoted `e(T)`) is the number of edges in
    $E \setminus T$ that are externally active with respect to `T` and `L`.
    Then [4]_ [5]_:

    .. math::

        T_G(x, y) = \sum_{T \text{ a spanning tree of } G} x^{i(T)} y^{e(T)}

    Def 3 (deletion-contraction recurrence): For `G` an undirected graph, `G-e`
    the graph obtained from `G` by deleting edge `e`, `G/e` the graph obtained
    from `G` by contracting edge `e`, `k(G)` the number of cut-edges of `G`,
    and `l(G)` the number of self-loops of `G`:

    .. math::
        T_G(x, y) = \begin{cases}
           x^{k(G)} y^{l(G)}, & \text{if all edges are cut-edges or self-loops} \\
           T_{G-e}(x, y) + T_{G/e}(x, y), & \text{otherwise, for an arbitrary edge $e$ not a cut-edge or loop}
        \end{cases}

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    instance of `sympy.core.add.Add`
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

    Edge contraction is defined and deletion-contraction is introduced in [6]_.
    Combinatorial meaning of the coefficients is introduced in [7]_.
    Universality, properties, and applications are discussed in [8]_.

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
    .. [5] A. Nešetril, J. Goodall,
       "Graph invariants, homomorphisms, and the Tutte polynomial"
       https://iuuk.mff.cuni.cz/~andrew/Tutte.pdf
    .. [6] D. B. West,
       "Introduction to Graph Theory," p. 84
    .. [7] G. Coutinho,
       "A brief introduction to the Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://homepages.dcc.ufmg.br/~gabriel/seminars/coutinho_tuttepolynomial_seminar.pdf
    .. [8] J. A. Ellis-Monaghan, C. Merino,
       "Graph polynomials and their applications I: The Tutte polynomial"
       Structural Analysis of Complex Networks, 2011
       https://arxiv.org/pdf/0803.3079.pdf
    """
    import sympy

    x, y = sympy.symbols("x y")
    # Attributes and contraction history cannot affect the polynomial.
    # Preserve the complete multigraph incidence structure, including loops.
    H = nx.MultiGraph()
    H.add_nodes_from(G)
    H.add_edges_from(G.edges())
    coefficients = _tutte_block_coefficients(H)
    return sympy.Add(*(value * x**i * y**j for (i, j), value in coefficients.items()))


@not_implemented_for("directed")
@nx._dispatchable
def chromatic_polynomial(G):
    r"""Returns the chromatic polynomial of `G`

    This function factors over biconnected blocks and computes each factor
    using iterative deletion-contraction. Forests, cycles and complete graphs
    use their closed forms. Intermediate coefficients are exact integers.

    The chromatic polynomial `X_G(x)` is a fundamental graph polynomial
    invariant in one variable. Evaluating `X_G(k)` for an natural number `k`
    enumerates the proper k-colorings of `G`.

    There are several equivalent definitions; here are three:

    Def 1 (explicit formula):
    For `G` an undirected graph, `c(G)` the number of connected components of
    `G`, `E` the edge set of `G`, and `G(S)` the spanning subgraph of `G` with
    edge set `S` [1]_:

    .. math::

        X_G(x) = \sum_{S \subseteq E} (-1)^{|S|} x^{c(G(S))}


    Def 2 (interpolating polynomial):
    For `G` an undirected graph, `n(G)` the number of vertices of `G`, `k_0 = 0`,
    and `k_i` the number of distinct ways to color the vertices of `G` with `i`
    unique colors (for `i` a natural number at most `n(G)`), `X_G(x)` is the
    unique Lagrange interpolating polynomial of degree `n(G)` through the points
    `(0, k_0), (1, k_1), \dots, (n(G), k_{n(G)})` [2]_.


    Def 3 (chromatic recurrence):
    For `G` an undirected graph, `G-e` the graph obtained from `G` by deleting
    edge `e`, `G/e` the graph obtained from `G` by contracting edge `e`, `n(G)`
    the number of vertices of `G`, and `e(G)` the number of edges of `G` [3]_:

    .. math::
        X_G(x) = \begin{cases}
           x^{n(G)}, & \text{if $e(G)=0$} \\
           X_{G-e}(x) - X_{G/e}(x), & \text{otherwise, for an arbitrary edge $e$}
        \end{cases}

    This formulation is also known as the Fundamental Reduction Theorem [4]_.


    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    instance of `sympy.core.add.Add`
        A Sympy expression representing the chromatic polynomial for `G`.

    Examples
    --------
    >>> C = nx.cycle_graph(5)
    >>> nx.chromatic_polynomial(C)
    x**5 - 5*x**4 + 10*x**3 - 10*x**2 + 4*x

    >>> G = nx.complete_graph(4)
    >>> nx.chromatic_polynomial(G)
    x**4 - 6*x**3 + 11*x**2 - 6*x

    Notes
    -----
    Interpretation of the coefficients is discussed in [5]_. Several special
    cases are listed in [2]_.

    The chromatic polynomial is a specialization of the Tutte polynomial; in
    particular, ``X_G(x) = (-1)**(n-c) * x**c * T_G(1-x, 0)``, where
    ``n`` is the number of vertices and ``c`` the number of connected
    components [6]_.

    The chromatic polynomial may take negative arguments, though evaluations
    may not have chromatic interpretations. For instance, ``(-1)**n * X_G(-1)``
    enumerates the acyclic orientations of `G`, where ``n`` is the number of
    vertices [7]_.

    References
    ----------
    .. [1] D. B. West,
       "Introduction to Graph Theory," p. 222
    .. [2] E. W. Weisstein
       "Chromatic Polynomial"
       MathWorld--A Wolfram Web Resource
       https://mathworld.wolfram.com/ChromaticPolynomial.html
    .. [3] D. B. West,
       "Introduction to Graph Theory," p. 221
    .. [4] J. Zhang, J. Goodall,
       "An Introduction to Chromatic Polynomials"
       https://math.mit.edu/~apost/courses/18.204_2018/Julie_Zhang_paper.pdf
    .. [5] R. C. Read,
       "An Introduction to Chromatic Polynomials"
       Journal of Combinatorial Theory, 1968
       https://math.berkeley.edu/~mrklug/ReadChromatic.pdf
    .. [6] W. T. Tutte,
       "Graph-polynomials"
       Advances in Applied Mathematics, 2004
       https://www.sciencedirect.com/science/article/pii/S0196885803000411
    .. [7] R. P. Stanley,
       "Acyclic orientations of graphs"
       Discrete Mathematics, 2006
       https://math.mit.edu/~rstan/pubs/pubfiles/18.pdf
    """
    import sympy

    x = sympy.Symbol("x")
    if nx.number_of_selfloops(G):
        return sympy.S.Zero

    # Parallel edges impose the same coloring constraint; attributes are unused.
    H = nx.Graph()
    H.add_nodes_from(G)
    H.add_edges_from(G.edges())
    coefficients = _chromatic_block_coefficients(H)
    return sympy.Add(*(value * x**degree for (degree,), value in coefficients.items()))
