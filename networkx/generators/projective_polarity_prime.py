"""
Projective Polarity Graph Generator.

This module constructs a graph based on the projective polarity model,
where nodes are derived from a finite projective space PG(m, q) over GF(q),
and edges are added based on modular dot-product orthogonality.

The special case of `m=2` produces the well-known
"Erdos-Renyi (ER) polarity graph", which is a diameter-2 graph
that serves as the basis for the PolarFly network topology.

Limitations
-----------
This version supports only prime `q` (i.e., GF(q) where q is a prime number),
due to the absence of an external Galois field library.

References
----------
[1] K. Lakhotia, M. Besta, L. Monroe, K. Isham, P. Iff, T. Hoefler, and F. Petrini.
    "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology."
    arXiv preprint arXiv:2208.01695, 2023.
    https://arxiv.org/pdf/2208.01695
[2] S. Mattheus, and F. Pavese.
    "A clique-free pseudorandom subgraph of the pseudo polarity
    graph"
    arXiv preprint arXiv:2105.03755, 2021.
    https://arxiv.org/pdf/2105.03755
"""

import itertools

import networkx as nx

__all__ = ["projective_polarity_graph"]


def _finite_field_vectors(m, q):
    r"""Generate the full finite field vector space GF(q)^(m+1).

    Parameters
    ----------
    m : int
        Projective space parameter; the vectors will be of length (`m`+1). Must be an integer ≥ 2.
    q : int
        Prime number defining the size of the Galois Field.

    Yields
    ------
    tuple of ints
        All vectors in GF(q)^(m+1) using standard modular arithmetic.
    """
    yield from itertools.product(range(q), repeat=m + 1)


def _normalize_projective(vector, q):
    r"""Normalize a vector in projective space over GF(q).

    Converts a `vector` to a canonical form by scaling so the first non-zero coordinate becomes 1.

    Parameters
    ----------
    vector : tuple of ints
        A `vector` in GF(q)^(m+1).
    q : int
        Prime number defining the field GF(q).

    Returns
    -------
    tuple of ints or None
        A normalized projective vector, or None if the input is the zero vector.

    Notes
    -----
    Normalization ensures uniqueness of projective points.

    Examples
    --------
    >>> from networkx.generators.projective_polarity_prime import _normalize_projective
    >>> vector = (2, 1, 0)
    >>> _normalize_projective(vector, 3)
    (1, 2, 0)
    """
    for v in vector:
        if v != 0:
            inv = pow(v, -1, q)  # modular inverse
            return tuple(int((x * inv) % q) for x in vector)
    return None  # skip zero vector


def _projective_space(m, q):
    r"""Generate the projective space PG(m, q) over GF(q).

    Parameters
    ----------
    m : int
        Projective space dimension. Must be an integer ≥ 2.
    q : int
        Prime number defining the field GF(q).

    Returns
    -------
    list of tuples
        A list of normalized vectors representing PG(m, q) points.

    Notes
    -----
    Projective points differing by a scalar multiple are represented uniquely.
    The zero vector is excluded.

    Examples
    --------
    >>> from networkx.generators.projective_polarity_prime import _projective_space
    >>> PG = _projective_space(2, 3)
    >>> len(PG)
    13
    >>> PG[0]
    (0, 0, 1)
    """
    seen = set()
    PG = []
    for vector in _finite_field_vectors(m, q):
        if all(x == 0 for x in vector):
            continue
        norm = _normalize_projective(vector, q)
        if norm is not None and norm not in seen:
            seen.add(norm)
            PG.append(norm)
    return PG


def projective_polarity_graph(m, q):
    r"""Generate an projective polarity graph from the projective space PG(m, q).

    Constructs an undirected graph where each node is a point in PG(m, q),
    and edges connect orthogonal pairs (under modular dot product mod `q`).

    Parameters
    ----------
    m : int
        Dimension of the projective space PG(m, q). Must be an integer ≥ 2.
    q : int
        Prime number defining GF(q). Must be prime (not a prime power).

    Returns
    -------
    G : networkx.Graph
        An undirected graph representing the projective polarity structure.

    Raises
    ------
    ValueError
        If `q` is not a prime number or if `m` is not an integer ≥ 2.

    Notes
    -----
    This implementation uses modular arithmetic and only supports prime `q`.

    For `m = 2`, the resulting graph corresponds to the well-known
    Erdős–Rényi (ER) polarity graph, which is a 2-diameter topology that
    asymptotically reaches the Moore bound on the number of nodes for a given
    degree and diameter. This case also underlies the PolarFly data center
    network topology [1].

    For `m > 2`, the generalized projective polarity graphs maintain strong
    connectivity, near-regularity and pseudorandom-like properties while remaining low-diameter
    structures, though not necessarily of diameter 2. These higher-dimensional
    variants have been studied as pseudorandom constructions, particularly their induced subgraphs [2].

    Examples
    --------
    >>> G = projective_polarity_graph(2, 3)
    >>> nx.diameter(G)
    2
    >>> nx.is_connected(G)
    True
    """
    import numpy as np

    # Check q is prime
    if q < 2 or any(q % i == 0 for i in range(2, int(q**0.5) + 1)):
        raise ValueError(
            "This implementation only supports prime q (not prime powers)."
        )

    # check m is an integer ≥ 2
    if not isinstance(m, int) or m < 2:
        raise ValueError("Parameter m must be an integer ≥ 2.")

    G = nx.Graph()
    PG = _projective_space(m, q)

    for u in PG:
        G.add_node(u)

    pg_array = np.array(PG, dtype=int)

    for i in range(len(PG)):
        for j in range(i + 1, len(PG)):
            if int(np.dot(pg_array[i], pg_array[j])) % q == 0:
                G.add_edge(PG[i], PG[j])

    return G
