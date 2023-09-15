"""Functions related to Kemeny's constant of a graph."""

import networkx as nx
from networkx.utils import not_implemented_for

__all__ = [
    "kemeny_constant",
]

@nx._dispatch(edge_attrs="weight")
def kemeny_constant(G, weight=None):
    """Returns Kemeny's constant of the given graph.

    *Kemeny's constant* of a graph can be computed by regarding the graph
    as a Markov chain. Kemeny's constant is then the expected number of time steps
    to transition from a starting state i to a random destination state
    sampled from the Markov chain's stationary distribution.
    Kemeny's constant is independent of the chosen initial state [1]_.

    If weight is not provided, then a weight of 1 is used for all edges.

    Parameters
    ----------
    G : NetworkX graph

    weight : string or None, optional (default=None)
       The edge data key used to compute the resistance distance.
       If None, then each edge has weight 1.

    Returns
    -------
    K : float
        Kemeny's constant of the graph `G`.

    Raises
    ------
    NetworkXError
        If the graph `G` is directed.

    NetworkXError
        If `G` does not contain any nodes.

    Examples
    --------
    >>> G = nx.complete_graph(5)
    >>> nx.kemeny_constant(G)
    3.2

    Notes
    -----
    The implementation is based on equation (3.3) in [2]_. Self-loops are ignored.
    Multi-edges are contracted in one edge with weight equal to the sum of the weights.

    References
    ----------
    .. [1] Wikipedia
       "Kemeny's constant."
       https://en.wikipedia.org/wiki/Kemeny%27s_constant
    .. [2] Lovász L.
        Random walks on graphs: A survey.
        Paul Erdös is Eighty, vol. 2, Bolyai Society,
        Mathematical Studies, Keszthely, Hungary (1993), pp. 1-46
    """

    if len(G) == 0:
        msg = "Graph G must contain at least one node."
        raise nx.NetworkXError(msg)
    elif nx.is_directed(G):
        msg = "Graph G must be undirected."
        raise nx.NetworkXError(msg)

    # Compute matrix H = D^-1/2 A D^-1/2
    A = nx.adjacency_matrix(G)
    n, m = A.shape
    diags = A.sum(axis=1)
    with sp.errstate(divide="ignore"):
        diags_sqrt = 1.0 / np.sqrt(diags)
    diags_sqrt[np.isinf(diags_sqrt)] = 0
    DH = sp.sparse.csr_array(sp.sparse.spdiags(diags_sqrt, 0, m, n, format="csr"))
    H = DH @ (A @ DH)

    # Compute eigenvalues of H
    eig = sp.linalg.eigvalsh(H.todense())
    eig = sorted(eig)
    print(eig)
    
    # Compute Kemeny's constant
    K = 0
    for i in range(n-1):
        K += 1 / (1 - eig[i])
    return K
