"""
ER Polarity Graph Generator.

This module constructs a graph based on the ER polarity model,
where nodes are derived from a finite projective space PG(m, q) over GF(q),
and edges are added based on projective orthogonality.

References
----------
[1] K. Lakhotia, M. Besta, L. Monroe, K. Isham, P. Iff, T. Hoefler, and F. Petrini.
    "PolarFly: A Cost-Effective and Flexible Low-Diameter Topology."
    arXiv preprint arXiv:2208.01695, 2023.
    https://arxiv.org/pdf/2208.01695
"""

import galois
import itertools
import networkx as nx
import numpy as np

def finite_field_vectors(m, q):
    r"""Generate the full finite field vector space GF(q)^(m+1).

    Parameters
    ----------
    m : int
        Projective space parameter; the vectors will be of length (m+1).
    q : int
        Prime power (q = p^k) defining the size of the Galois Field.

    Returns
    -------
    list of tuples
        All vectors in GF(q)^(m+1).
    """
    GF = galois.GF(q)
    return list(itertools.product(GF.elements, repeat=m + 1))

def normalize_projective(vector, GF):
    r"""Normalize a vector in projective space over GF(q).

    Converts a vector to a canonical form by scaling
    so the first non-zero coordinate becomes 1.

    Parameters
    ----------
    vector : tuple
        A vector in GF(q)^(m+1).
    GF : galois.GF
        A Galois Field instance.

    Returns
    -------
    tuple
        A normalized vector representing a projective point,
        or None if the vector is zero.

    Notes
    -----
    Ensures that vectors differing by a nonzero scalar are represented by a unique canonical form.

    Examples
    --------
    >>> from er_polarity_graph import normalize_projective
    >>> import galois
    >>> GF = galois.GF(3)
    >>> vector = tuple(GF([2, 1, 0]))
    >>> normalize_projective(vector, GF)
    (GF(1, order=3), GF(2, order=3), GF(0, order=3))
    """
    for v in vector:
        if v != GF(0):
            inv = v ** -1
            return tuple(x * inv for x in vector)
    return None  # zero vector

def projective_space(m, q):
    r"""Generate the projective space PG(m, q) from GF(q)^(m+1).

    Parameters
    ----------
    m : int
        Projective dimension; vectors are of length (m+1).
    q : int
        Prime power, defining the base field GF(q).

    Returns
    -------
    PG : list of tuples
        Each element is a tuple (int_key, normalized_vector), where:
        - int_key : tuple of ints
            Hashable identifier of the projective point.
        - normalized_vector : tuple of galois field elements
            Canonical representation of a projective point in GF(q)^(m+1).

    Notes
    -----
    The zero vector is excluded.
    Points differing by scalar multiplication are identified as the same.

    Examples
    --------
    >>> from er_polarity_graph import projective_space
    >>> PG = projective_space(2, 3)
    >>> len(PG)
    13
    >>> PG[0]
    ((0, 0, 1), (GF(0, order=3), GF(0, order=3), GF(1, order=3)))
    """
    GF = galois.GF(q)
    PG = []
    seen = set()
    for vector in finite_field_vectors(m, q):
        if all(x == GF(0) for x in vector):
            continue
        norm_vec = normalize_projective(vector, GF)
        if norm_vec is None:
            continue
        int_key = tuple(int(x) for x in norm_vec)
        if int_key not in seen:
            seen.add(int_key)
            PG.append((int_key, norm_vec))
    return PG

def er_polarity_graph(m, q):
    r"""Generate an ER polarity graph from the projective space PG(m, q).

    Constructs a graph where each node corresponds to a projective point,
    and edges connect orthogonal pairs based on the dot product in GF(q).

    Parameters
    ----------
    m : int
        Projective space parameter (PG(m, q)).
    q : int
        Prime power for GF(q). q must be a power of a prime.

    Returns
    -------
    G : networkx.Graph
        An undirected graph representing the ER polarity structure.

    Raises
    ------
    ValueError
        If generated ER polarity graph is not connected.

    Notes
    -----
    Two nodes are connected if their dot product (computed in GF(q)) is zero.
    This corresponds to projective orthogonality.

    Examples
    --------
    >>> G = er_polarity_graph(2, 3)
    >>> nx.diameter(G)
    2
    >>> nx.is_connected(G)
    True
    """
    G = nx.Graph()
    GF = galois.GF(q)
    PG = projective_space(m, q)

    # Add nodes
    for int_key, _ in PG:
        G.add_node(int_key)

    # Add edges
    for i in range(len(PG)):
        key_u, vec_u = PG[i]
        u = GF(vec_u)
        for j in range(i + 1, len(PG)):
            key_v, vec_v = PG[j]
            v = GF(vec_v)
            if np.sum(u * v) == GF(0):
                G.add_edge(key_u, key_v)

    # Raise exception if disconnected
    if not nx.is_connected(G):
        raise ValueError("Generated ER polarity graph is not connected.")
    return G