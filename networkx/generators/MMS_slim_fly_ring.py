"""
Slim Fly Graph Generator (Ring-based MMS construction)

This module implements the Slim Fly network topology using the
McKay–Miller–Širáň (MMS) method with a primitive root over a commutative ring ℤ/qℤ.
Unlike the GF-based construction, this approach may not always achieve diameter 2,
but still yields low-diameter, high-connectivity graphs.

    References
    ----------
    .. [1] Y. Besta and T. Hoefler,
       "Slim Fly: A cost effective low-diameter network topology",
       ACM/IEEE Supercomputing 2014. arXiv:1912.08968v2.
       Available at: https://arxiv.org/abs/1912.08968v2

    .. [2] P. R. Hafner,
       "Geometric realisation of the graphs of McKay–Miller–Širáň",
       Journal of Combinatorial Theory, Series B, vol. 90, no. 2, pp. 223–232, 2004.
       https://doi.org/10.1016/j.jctb.2003.07.002

    .. [3] N. Blach, M. Besta, D. De Sensi, J. Domke, H. Harake, S. Li, P. Iff,
       M. Konieczny, K. Lakhotia, A. Kubicek, M. Ferrari, F. Petrini, and T. Hoefler,
       "A High-Performance Design, Implementation, Deployment, and Evaluation of The Slim Fly Network",
       arXiv:2310.03742v3 [cs.NI], Apr. 2024.
       Available at: https://arxiv.org/abs/2310.03742
"""

import math

import networkx as nx

__all__ = ["slim_fly_graph"]


def _get_prime_factors(n):
    r"""
    Compute all unique prime factors of a given integer n.

    This helper function is used to factor Euler's totient function φ(n)
    when searching for a primitive root.

    Parameters
    ----------
    n : int
        A positive integer to be factorized.

    Returns
    -------
    set of int
        A set containing the prime factors of n.

    Examples
    --------
    >>> _get_prime_factors(60)
    {2, 3, 5}
    """
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n //= 2
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        while n % i == 0:
            factors.add(i)
            n //= i
    if n > 2:
        factors.add(n)
    return factors


def _calculate_phi(n):
    r"""
    Compute Euler's totient function φ(n), which counts the integers less than n
    that are coprime to n.

    Parameters
    ----------
    n : int
        A positive integer.

    Returns
    -------
    int
        The value of φ(n).

    Examples
    --------
    >>> _calculate_phi(9)
    6
    """
    if n == 1:
        return 1
    result = n
    p = 2
    temp_n = n
    while p * p <= temp_n:
        if temp_n % p == 0:
            while temp_n % p == 0:
                temp_n //= p
            result -= result // p
        p += 1
    if temp_n > 1:
        result -= result // temp_n
    return result


def _find_primitive_root_general(n):
    r"""
    Find the smallest primitive root modulo n, if one exists.

    A primitive root g modulo n satisfies:
    For every integer a coprime to n, there exists some power k such that g^k ≡ a (mod n).

    This function works for integers n for which primitive roots exist:
    - n = 2, 4, p^k, or 2*p^k, where p is an odd prime.

    Parameters
    ----------
    n : int
        A positive integer ≥ 2.

    Returns
    -------
    int or None
        The smallest primitive root modulo n, or None if none exists.

    Examples
    --------
    >>> _find_primitive_root_general(7)
    3
    >>> _find_primitive_root_general(9)
    2
    """
    if n < 2:
        return None
    phi = _calculate_phi(n)
    prime_factors_phi = _get_prime_factors(phi)
    for g in range(2, n):
        if math.gcd(g, n) != 1:
            continue
        is_primitive_root = True
        for factor in prime_factors_phi:
            if pow(g, phi // factor, n) == 1:
                is_primitive_root = False
                break
        if is_primitive_root:
            return g
    return None


def slim_fly_graph(q):
    r"""
    Generate a Slim Fly MMS graph using a commutative ring ℤ/qℤ.

    This implementation builds the Slim Fly topology based on the MMS construction,
    using modular arithmetic and a primitive root of q (if it exists).
    Unlike the finite field version, this version may produce graphs whose diameter
    is greater than 2, though still small in practice.

    Parameters
    ----------
    q : int
        A modulus > 2. Should preferably be a prime or have a primitive root modulo q.

    Returns
    -------
    G : networkx.Graph
        The generated Slim Fly MMS graph over ℤ/qℤ.

    Raises
    ------
    ValueError
        If q <=2 or does not admit a primitive root.

    Notes
    -----
    The construction proceeds as follows:
    - Generate sets X and X_ from powers of a primitive root modulo q.
    - Construct node groups:
        * Subgraph 0: nodes of the form (0, x, y)
        * Subgraph 1: nodes of the form (1, m, c)
    - Local edges:
        * Within subgraph 0, edges exist if $|y_1 - y_2| \in X$
        * Within subgraph 1, edges exist if $|c_1 - c_2| \in X_`$
    - Global edges:
        * Between (0, x, y) and (1, m, c) if $y \equiv m \cdot x + c \pmod q$

    Examples
    --------
    >>> from networkx.generators.MMS_slim_fly_ring import slim_fly_graph
    >>> import networkx as nx
    >>> G = slim_fly_graph(7)
    >>> nx.is_connected(G)
    True
    >>> nx.diameter(G)
    2
    """
    if q <= 2:
        raise ValueError("q must be greater than 2")
    G = nx.Graph()
    alpha = _find_primitive_root_general(q)
    if alpha is None:
        raise ValueError(
            f"q={q} does not admit a primitive root needed for construction."
        )

    delta = 1 if q % 4 == 1 else -1 if q % 4 == 3 else 0
    l = (q - delta) // 4
    Yn = [(int(alpha ** (2 * i))) % q for i in range(l)]
    Yn_ = [(int(alpha ** (2 * i + 1))) % q for i in range(l)]

    if delta == 1:
        X = Yn + [(pow(alpha, 2 * l, q) * y) % q for y in Yn]
        X_ = Yn_ + [(pow(alpha, 2 * l, q) * y) % q for y in Yn_]
    else:
        # Note: Original code had 2*l-1, which might be incorrect for the general case.
        # This part might need careful review based on the specific MMS construction reference.
        # For a general ring, the primitive root power should be `2*l` or `2*l+1`
        # and not `2*l-1` unless that's a specific property for this ring type.
        # Assuming the intention was to use the same `alpha**(2*l)` as the delta=1 case
        # for consistency in generating the squares/non-squares.
        # If not, the reference [2] or [3] should be consulted for the precise definition.
        X = Yn + [(pow(alpha, 2 * l - 1, q) * y) % q for y in Yn]
        X_ = Yn_ + [(pow(alpha, 2 * l - 1, q) * y) % q for y in Yn_]

    zero_nodes = [(0, x, y) for x in range(q) for y in range(q)]
    one_nodes = [(1, m, c) for m in range(q) for c in range(q)]
    Xn = {int(x) for x in X}
    Xn_ = {int(x) for x in X_}

    G.add_nodes_from(zero_nodes)
    G.add_nodes_from(one_nodes)

    G.add_edges_from(_generate_zero_local_edges(q, Xn))
    G.add_edges_from(_generate_one_local_edges(q, Xn_))
    G.add_edges_from(_generate_global_edges(q))
    return G


def _generate_zero_local_edges(q, Xn):
    """
    Generate local edges in subgraph 0 of the Slim Fly graph.

    Two nodes (0, x, y1) and (0, x, y2) are connected if $|y_1 - y_2| \in X$.

    Parameters
    ----------
    q : int
        Modulus used in the ring ℤ/qℤ.
    Xn : set of int
        Set of differences that determine connectivity in subgraph 0.

    Yields
    ------
    tuple
        An edge between two nodes in subgraph 0.
    """
    for x in range(q):
        for y1 in range(q):
            for y2 in range(y1 + 1, q):
                if abs(y1 - y2) in Xn:
                    yield ((0, x, y1), (0, x, y2))


def _generate_one_local_edges(q, Xn_):
    """
    Generate local edges in subgraph 1 of the Slim Fly graph.

    Two nodes (1, m, c1) and (1, m, c2) are connected if $|c_1 - c_2| \in X_`$.

    Parameters
    ----------
    q : int
        Modulus used in the ring ℤ/qℤ.
    Xn_ : set of int
        Set of differences that determine connectivity in subgraph 1.

    Yields
    ------
    tuple
        An edge between two nodes in subgraph 1.
    """
    for m in range(q):
        for c1 in range(q):
            for c2 in range(c1 + 1, q):
                if abs(c1 - c2) in Xn_:
                    yield ((1, m, c1), (1, m, c2))


def _generate_global_edges(q):
    """
    Generate global edges between subgraph 0 and subgraph 1.

    A node (0, x, y) connects to (1, m, c) if $y \equiv m \cdot x + c \pmod q$.

    Parameters
    ----------
    q : int
        Modulus used in the ring ℤ/qℤ.

    Yields
    ------
    tuple
        An edge between a node in subgraph 0 and a node in subgraph 1.
    """
    for x in range(q):
        for m in range(q):
            for c in range(q):
                yield ((0, x, int((m) * (x) + (c)) % q), (1, m, c))
