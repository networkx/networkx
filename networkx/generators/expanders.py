"""Provides explicit constructions of expander graphs.

"""
import itertools

import networkx as nx
from networkx.utils.misc import pairwise

__all__ = [
    "margulis_gabber_galil_graph",
    "chordal_cycle_graph",
    "paley_graph",
    "maybe_regular_expander",
    "is_regular_expander",
    "random_regular_expander",
]


# Other discrete torus expanders can be constructed by using the following edge
# sets. For more information, see Chapter 4, "Expander Graphs", in
# "Pseudorandomness", by Salil Vadhan.
#
# For a directed expander, add edges from (x, y) to:
#
#     (x, y),
#     ((x + 1) % n, y),
#     (x, (y + 1) % n),
#     (x, (x + y) % n),
#     (-y % n, x)
#
# For an undirected expander, add the reverse edges.
#
# Also appearing in the paper of Gabber and Galil:
#
#     (x, y),
#     (x, (x + y) % n),
#     (x, (x + y + 1) % n),
#     ((x + y) % n, y),
#     ((x + y + 1) % n, y)
#
# and:
#
#     (x, y),
#     ((x + 2*y) % n, y),
#     ((x + (2*y + 1)) % n, y),
#     ((x + (2*y + 2)) % n, y),
#     (x, (y + 2*x) % n),
#     (x, (y + (2*x + 1)) % n),
#     (x, (y + (2*x + 2)) % n),
#
def margulis_gabber_galil_graph(n, create_using=None):
    r"""Returns the Margulis-Gabber-Galil undirected MultiGraph on `n^2` nodes.

    The undirected MultiGraph is regular with degree `8`. Nodes are integer
    pairs. The second-largest eigenvalue of the adjacency matrix of the graph
    is at most `5 \sqrt{2}`, regardless of `n`.

    Parameters
    ----------
    n : int
        Determines the number of nodes in the graph: `n^2`.
    create_using : NetworkX graph constructor, optional (default MultiGraph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : graph
        The constructed undirected multigraph.

    Raises
    ------
    NetworkXError
        If the graph is directed or not a multigraph.

    """
    G = nx.empty_graph(0, create_using, default=nx.MultiGraph)
    if G.is_directed() or not G.is_multigraph():
        msg = "`create_using` must be an undirected multigraph."
        raise nx.NetworkXError(msg)

    for x, y in itertools.product(range(n), repeat=2):
        for u, v in (
            ((x + 2 * y) % n, y),
            ((x + (2 * y + 1)) % n, y),
            (x, (y + 2 * x) % n),
            (x, (y + (2 * x + 1)) % n),
        ):
            G.add_edge((x, y), (u, v))
    G.graph["name"] = f"margulis_gabber_galil_graph({n})"
    return G


def chordal_cycle_graph(p, create_using=None):
    """Returns the chordal cycle graph on `p` nodes.

    The returned graph is a cycle graph on `p` nodes with chords joining each
    vertex `x` to its inverse modulo `p`. This graph is a (mildly explicit)
    3-regular expander [1]_.

    `p` *must* be a prime number.

    Parameters
    ----------
    p : a prime number

        The number of vertices in the graph. This also indicates where the
        chordal edges in the cycle will be created.

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : graph
        The constructed undirected multigraph.

    Raises
    ------
    NetworkXError

        If `create_using` indicates directed or not a multigraph.

    References
    ----------

    .. [1] Theorem 4.4.2 in A. Lubotzky. "Discrete groups, expanding graphs and
           invariant measures", volume 125 of Progress in Mathematics.
           Birkhäuser Verlag, Basel, 1994.

    """
    G = nx.empty_graph(0, create_using, default=nx.MultiGraph)
    if G.is_directed() or not G.is_multigraph():
        msg = "`create_using` must be an undirected multigraph."
        raise nx.NetworkXError(msg)

    for x in range(p):
        left = (x - 1) % p
        right = (x + 1) % p
        # Here we apply Fermat's Little Theorem to compute the multiplicative
        # inverse of x in Z/pZ. By Fermat's Little Theorem,
        #
        #     x^p = x (mod p)
        #
        # Therefore,
        #
        #     x * x^(p - 2) = 1 (mod p)
        #
        # The number 0 is a special case: we just let its inverse be itself.
        chord = pow(x, p - 2, p) if x > 0 else 0
        for y in (left, right, chord):
            G.add_edge(x, y)
    G.graph["name"] = f"chordal_cycle_graph({p})"
    return G


def paley_graph(p, create_using=None):
    r"""Returns the Paley $\frac{(p-1)}{2}$ -regular graph on $p$ nodes.

    The returned graph is a graph on $\mathbb{Z}/p\mathbb{Z}$ with edges between $x$ and $y$
    if and only if $x-y$ is a nonzero square in $\mathbb{Z}/p\mathbb{Z}$.

    If $p \equiv 1  \pmod 4$, $-1$ is a square in $\mathbb{Z}/p\mathbb{Z}$ and therefore $x-y$ is a square if and
    only if $y-x$ is also a square, i.e the edges in the Paley graph are symmetric.

    If $p \equiv 3 \pmod 4$, $-1$ is not a square in $\mathbb{Z}/p\mathbb{Z}$ and therefore either $x-y$ or $y-x$
    is a square in $\mathbb{Z}/p\mathbb{Z}$ but not both.

    Note that a more general definition of Paley graphs extends this construction
    to graphs over $q=p^n$ vertices, by using the finite field $F_q$ instead of $\mathbb{Z}/p\mathbb{Z}$.
    This construction requires to compute squares in general finite fields and is
    not what is implemented here (i.e `paley_graph(25)` does not return the true
    Paley graph associated with $5^2$).

    Parameters
    ----------
    p : int, an odd prime number.

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    G : graph
        The constructed directed graph.

    Raises
    ------
    NetworkXError
        If the graph is a multigraph.

    References
    ----------
    Chapter 13 in B. Bollobas, Random Graphs. Second edition.
    Cambridge Studies in Advanced Mathematics, 73.
    Cambridge University Press, Cambridge (2001).
    """
    G = nx.empty_graph(0, create_using, default=nx.DiGraph)
    if G.is_multigraph():
        msg = "`create_using` cannot be a multigraph."
        raise nx.NetworkXError(msg)

    # Compute the squares in Z/pZ.
    # Make it a set to uniquify (there are exactly (p-1)/2 squares in Z/pZ
    # when is prime).
    square_set = {(x**2) % p for x in range(1, p) if (x**2) % p != 0}

    for x in range(p):
        for x2 in square_set:
            G.add_edge(x, (x + x2) % p)
    G.graph["name"] = f"paley({p})"
    return G


def maybe_regular_expander(d, n):
    r"""Utility for creating a random regular expander.

    Returns a random $d$-regular graph on $n$ nodes which is an expander graph with very good probability.

    Parameters
    ----------
    d : int
      The degree of each node.
    n : integer
      The number of nodes.

    Notes
    -----
    The nodes are numbered from $0$ to $n - 1$.

    The graph is generated by taking $d / 2$ random independent cycles.

    Joel Friedman proved that in this model the resulting graph is an expander with probability $1 - O(n^{-\tau})$ where $\tau = \lceil (\sqrt{d - 1}) / 2 \rceil - 1$. [1]_

    Examples
    --------
    >>> G = nx.maybe_regular_expander(6, 200)

    Returns
    -------
    G : graph
        The constructed undirected graph.

    Raises
    ------
    NetworkXError
        If $d % 2 != 0$ as the degree must be even.
        If $n - 1$ is less than $ 2d $ as the graph is complete at most.

    References
    ----------
    .. [1] Joel Friedman,
       A Proof of Alon’s Second Eigenvalue Conjecture and Related Problems, 2004
       https://arxiv.org/abs/cs/0405020

    """

    import numpy as np

    if not (isinstance(n, int) and n > 0):
        raise nx.NetworkXError("n must be a positive integer")

    if not (d >= 2):
        raise nx.NetworkXError("d must be greater than or equal to 2")

    if not (isinstance(d, int) and d % 2 == 0):
        raise nx.NetworkXError("d must be even")

    if not (n - 1 >= d):
        raise nx.NetworkXError(
            f"There is not enough room for {d//2} independent cycles in a graph of size {n}"
        )

    G = nx.Graph()
    G.add_nodes_from(range(n))

    # Faster than random.permutation(n) since there are only
    # (n-1)! distinct cycles against n! permutations of size n
    random_cycle = lambda n: np.concatenate((np.random.permutation(n - 1), [n - 1]))

    if n < 2:
        return G

    cycles = []
    edges = set()

    # Create d / 2 cycles
    for i in range(d // 2):
        # Make sure the cycles are independent to have a regular graph
        while len(edges) != (i + 1) * n:
            cycle = random_cycle(n)

            cycle_edges = list(pairwise(cycle, cyclic=True))
            cycle_edges_sorted = [tuple(sorted(x)) for x in cycle_edges]
            new_edges = {*edges, *cycle_edges_sorted}

            # If the new cycle has no edges in common with previous cycles
            # then add it to the list otherwise try again
            if len(new_edges) == len(edges) + n:
                cycles.append(cycle)
                edges = new_edges

    G.add_edges_from(list(edges))

    return G


def is_regular_expander(G: nx.Graph, *, epsilon=0):
    """Determines whether the graph G is a regular expander.

    More precisely, checks whether the graph is a regular $(n, d, \lambda)$-expander with $\lambda$ close to the Alon-Boppana bound and given by $\lambda = 2 \sqrt{d - 1} + \epsilon$. [1]_

    In the case where $\epsilon = 0 $ then if the graph successfully passes the test it is a Ramanujan graph. [2]_

    Parameters
    ----------
    G : NetworkX graph
    epsilon : int, float, default=0

    Returns
    -------
    bool
        Whether the given graph is a regular $(n, d, \lambda)$-expander where $\lambda = 2 \sqrt{d - 1} + \epsilon$.

    Examples
    --------
    >>> G = nx.random_regular_expander(4, 20)
    >>> nx.is_regular_expander(G)
    True

    References
    ----------
    .. [1] Alon-Boppana bound, https://en.wikipedia.org/wiki/Alon%E2%80%93Boppana_bound
    .. [2] Ramanujan graphs, https://en.wikipedia.org/wiki/Ramanujan_graph

    """

    import numpy as np

    if not (isinstance(epsilon, (int, float)) and epsilon >= 0):
        raise nx.NetworkXError("epsilon must be non negative")

    if not nx.is_regular(G):
        return False

    d = list(G.degree)[0][1]

    A = nx.adjacency_matrix(G)
    eigen_vals, _ = np.linalg.eig(A.toarray())

    # lambda2 is the second biggest eigenvalue
    lambda2 = sorted(eigen_vals, reverse=True)[1]

    return lambda2 < 2 ** np.sqrt(d - 1) + epsilon


def random_regular_expander(d, n, *, epsilon=0):
    r"""Returns a random regular expander graph on $n$ nodes with degree $d$.

    The returned graph is a $(n, d, \lambda)$-expander with
    $\lambda = 2 \sqrt{d - 1} + \epsilon$, close to the Alon-Boppana bound.

    In the case where $\epsilon = 0 $ it returns a Ramanujan graph.

    Parameters
    ----------
    d : int
      The degree of each node.
    n : integer
      The number of nodes.
    epsilon : int, float, default=0

    Examples
    --------
    >>> G = nx.random_regular_expander(4, 20)
    >>> nx.is_regular_expander(G)
    True

    Notes
    -----
    This loops over ``maybe_regular_expander`` and can be slow when $n$ is too big or $\epsilon$ too small.

    See Also
    --------
    maybe_regular_expander
    is_regular_expander

    """
    G = maybe_regular_expander(d, n)

    while not is_regular_expander(G, epsilon=epsilon):
        G = maybe_regular_expander(d, n)

    return G
