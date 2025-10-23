"""
Implementation of the KRV cut matching algorithm for finding sparsest cut.
"""

import math

import networkx as nx
from networkx.utils.decorators import not_implemented_for

from .utils import (
    build_flow_network,
    compute_mincut,
    flow_matching,
    generate_random_orthogonal_gaussian,
)

__all__ = ["sparse_cut", "sparsest_cut", "balanced_sparse_cut"]


@not_implemented_for("directed")
def sparse_cut(
    G,
    alpha,
    _s,
    _t,
    _seed=None,
    min_iterations=0,
    num_candidates=20,
    b=1 / 3,
    flow_func=None,
    **kwargs,
):
    r"""Given a graph `G` with n nodes, find a $b / 4\log^2(n)$ balanced `alpha`
    sparse cut in `G` or certify with high probability that every `b` balanced
    cut has expansion $O(alpha / \log^2(n))$.

    This algorithm has a running time of $O(log^2(n) (T_f + m / \alpha))$ for
    a graph `G` with $n$ nodes and `m` edges, and a flow function which runs
    in time $T_f$.

    Parameters
    ----------
    G : Networkx Graph

    alpha : float
        Upper bound for expansion of the returned cut

    _s : object
        Key for a super-source used in flow computations. Must satisfy `_s not in G`.

    _t : object
        Key for a super-sink used in flow computations. Must satisfy `_t not in G`.

    _seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    min_iterations : int
        Minimum number of iterations to run the cut-matching procedure.

    num_candidates : int
        Number of random unit vectors to consider during the algorithm. A higher
        value increases the quality of the cut or the confidence in the expansion
        guarantee, but decreases the running time.

    b : float
        Balance parameter for the expansion guarantee. If the first set returned
        is empty, then all b-balanced cuts in `G` have expansion at least `alpha`.
        Must be less than 1/2.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes
        in a capacitated graph. The function has to accept at least three
        parameters: a Graph or Digraph, a source node, and a target node.
        And return a residual network that follows NetworkX conventions
        (see Notes). If flow_func is None, the default maximum
        flow function (:meth:`preflow_push`) is used. The choice of the default function
        may change from version to version and should not be relied on. Default value:
        None.

    kwargs : Any other keyword parameter is passed to the function that
        computes the maximum flow.

    Returns
    -------
    tuple[set, set]
        A cut in `G` which has expansion at most `alpha`. If every `b` balanced cut in `G` has
        expansion $O(alpha / log^2(n))$, then the first set in the tuple will be empty.

    Raises
    ------
    NetworkXError
        If `flow_func` is specified but not callable, the algorithm raises a NetworkXError.

    NetworkXNotImplemented
        If the input graph is not undirected.

    Notes
    -----
    This algorithm follows the implementation in [1]_ with some slight
    modifications. In [1]_, the flow function used is an algorithm of
    Goldberg and Rao which runs in time $O(m^{3/2})$. This algorithm
    is not good for practical use. [2]_ found that in practice, preflow
    push is more efficient than the Unit Flow algorithm, a height-constrained
    variant of preflow-push which has near-linear theoretical complexity.

    The function used in the flow_func parameter has to return a residual
    network that follows NetworkX conventions:

    The residual network :samp:`R` from an input graph :samp:`G` has the
    same nodes as :samp:`G`. :samp:`R` is a DiGraph that contains a pair
    of edges :samp:`(u, v)` and :samp:`(v, u)` iff :samp:`(u, v)` is not a
    self-loop, and at least one of :samp:`(u, v)` and :samp:`(v, u)` exists
    in :samp:`G`.

    For each edge :samp:`(u, v)` in :samp:`R`, :samp:`R[u][v]['capacity']`
    is equal to the capacity of :samp:`(u, v)` in :samp:`G` if it exists
    in :samp:`G` or zero otherwise. If the capacity is infinite,
    :samp:`R[u][v]['capacity']` will have a high arbitrary finite value
    that does not affect the solution of the problem. This value is stored in
    :samp:`R.graph['inf']`. For each edge :samp:`(u, v)` in :samp:`R`,
    :samp:`R[u][v]['flow']` represents the flow function of :samp:`(u, v)` and
    satisfies :samp:`R[u][v]['flow'] == -R[v][u]['flow']`.

    The flow value, defined as the total flow into :samp:`t`, the sink, is
    stored in :samp:`R.graph['flow_value']`. Reachability to :samp:`t` using
    only edges :samp:`(u, v)` such that
    :samp:`R[u][v]['flow'] < R[u][v]['capacity']` induces a minimum
    :samp:`s`-:samp:`t` cut.

    Specific algorithms may store extra data in :samp:`R`.

    The function should supports an optional boolean parameter value_only. When
    True, it can optionally terminate the algorithm as soon as the maximum flow
    value and the minimum cut can be determined.

    Note that the resulting maximum flow may contain flow cycles,
    back-flow to the source, or some flow exiting the sink.
    These are possible if there are cycles in the network.

    References
    ----------
    .. [1] R. Khandekar, S. Rao, and U. Vazirani. Graph partitioning
            using single commodity flows. J. ACM, 56(4):1-15, 2009.

    .. [2] L. Gottesburn, N. Parotsidis, and M. P. Gutenburg. Practical
            Expander Decomposition. J. ESA, 32(61):1-17, 2024.
    """
    import numpy as np
    import scipy as sp

    if _seed is None:
        _seed = np.random.RandomState()
    if isinstance(_seed, int):
        _seed = np.random.RandomState(_seed)

    if flow_func is None:
        if kwargs:
            raise nx.NetworkXError(
                "You have to explicitly set a flow_func if"
                " you need to pass parameters via kwargs."
            )
        flow_func = nx.algorithms.flow.preflow_push
    if not callable(flow_func):
        raise nx.NetworkXError("flow_func must be callable")

    if _s in G or _t in G:
        raise nx.NetworkXError(
            "super-source node _s or super-sink node _t are already in G."
        )

    if b < 0 or b > 1 / 2:
        raise nx.NetworkXError("b must be between 0 and 0.5.")

    n = len(G)
    m = len(G.edges())
    T = math.ceil(20 + 10 * math.log(m) ** 2)

    index_to_vertex = dict(enumerate(G))
    vertex_to_index = {v: i for i, v in enumerate(G)}

    proj_flow_vecs = generate_random_orthogonal_gaussian(n, num_candidates, _seed=_seed)

    for _ in range(max(T, min_iterations)):
        norms = np.linalg.norm(proj_flow_vecs, axis=0)
        u = proj_flow_vecs[:, np.argmax(norms)]

        # Norm of u is an unbiased estimator of the potential.
        # See GPG'24 Practical Expander Decomposition
        if np.linalg.norm(u) ** 2 < 1 / 16 / n**3:
            return set(), set(G.nodes())

        # get cut from best vector
        u_argsorted = np.argsort(u)
        A = set(u_argsorted[: n // 2])
        B = set(u_argsorted[n // 2 :])
        A = {index_to_vertex[i.item()] for i in A}
        B = {index_to_vertex[i.item()] for i in B}

        # build flow network using G and A, B
        H = build_flow_network(G, _s, _t, A, B, math.ceil(1 / alpha), 1)

        # solve flow
        R = flow_func(H, _s, _t, **kwargs)
        if R.graph["flow_value"] < math.floor((1 / 2 - b / 4 / math.log(n) ** 2) * n):
            Q, S = compute_mincut(R, _t)
            return Q.intersection(set(G)), S.intersection(set(G))

        # get matching from flow
        matching = flow_matching(R, _s, _t)
        # complete dummy matching
        unmatched_A = [v for v in A if v not in matching]
        unmatched_B = [v for v in B if v not in matching]
        while unmatched_A and unmatched_B:
            a = unmatched_A.pop()
            b = unmatched_B.pop()
            matching[a] = b
            matching[b] = a
        # handle odd vertices
        if len(unmatched_A) == 1:
            matching[unmatched_A[0]] = unmatched_A[0]
        if len(unmatched_B) == 1:
            matching[unmatched_B[0]] = unmatched_B[0]

        rows = [vertex_to_index[m] for m in matching]
        cols = [vertex_to_index[m] for m in matching.values()]
        data = [0.5] * n

        # update across matching
        W = (
            0.5 * sp.sparse.identity(n)
            + sp.sparse.coo_array((data, (rows, cols)), (n, n)).tocsr()
        )
        proj_flow_vecs = W @ proj_flow_vecs
    return set(), set(G.nodes())


@not_implemented_for("directed")
def sparsest_cut(G, _s, _t, **kwargs):
    r"""Given a graph `G` with n nodes, find an $\alpha$ sparse cut in `G`
    such that `G` is an $\alpha / 4 \log(n)^2$ edge expander.

    This algorithm runs in time $O(\log(d) \log^2(n)(T_f + m / \alpha))$
    for a graph `G` with `n` nodes, `m` edges, and maximum degree `d`,
    and a flow function which runs in time $T_f$.

    Parameters
    ----------
    G : NetworkX Graph

    _s : object
        Key for super-source node added during flow computations. Must
        satisfy `_s not in G`.

    _t : object
        Key for super-sink node added during flow computations. Must
        satisfy `_t not in G`.

    kwargs : Any other keyword argument to be passed to the sparse_cut
        function.

    Returns
    -------
    tuple[set, set]
        An $\alpha$ sparse cut in `G` such that `G` is an $\alpha / 4 \log(n)^2$
        edge expander.

    Raises
    ------
    NetworkXNotImplemented
        If the input graph is not undirected

    See also
    --------
    :meth: `sparse_cut`
    :meth: `balanced_sparse_cut`
    """
    alpha = max(d for _, d in G.degree()) * math.log(len(G)) ** 2
    found_sparse = True
    best_cut_so_far = (set(), set(G.nodes()))
    while found_sparse:
        S, T = sparse_cut(G, alpha, _s, _t, b=0, **kwargs)
        if len(S) == 0 or len(T) == 0:
            found_sparse = False
            return best_cut_so_far
        best_cut_so_far = (S, T)
        alpha /= 2


@not_implemented_for("directed")
def balanced_sparse_cut(G, alpha, _s, _t, balance, **kwargs):
    r"""Given a graph `G` with n nodes, a sparsity parameter `alpha`, and a balance
    parameter `balance`, find an `alpha` sparse cut `balance` balanced cut, or
    certify that every `1/3` balanced cut in `G` has expansion at least
    $\alpha / 4 \log(n)^2$.

    This algorithm runs in time $O(log(n)^4 (T_f + m / \alpha))$, where m
    is the number of edges in `G` and $T_f$ is the time it takes to compute
    a single commodity max flow.

    Parameters
    ----------
    G : NetworkX Graph

    alpha : float
        Upper bound for the expansion of the returned cut, if any is returned.

    _s : object
        Key for super-source node added during flow computations. Must satisfy
        `_s not in G`.

    _t : object
        Key for super-sink node added during flow computations. Must satisfy
        `_t not in G`.

    balance : float
        A number between between 0 and 1/3, not inclusive, such that the
        returned cut (if any) will have size at least `balance * n`.

    kwargs : Any other keyword argument to be passed to the sparse_cut
        function.

    Returns
    -------
    tuple[set, set]
        A cut (S, T) such that either S is an `alpha` sparse cut of size at least
        `balance * n`, or `S` is empty and all sets of size `n / 3` in `G` have
        expansion at least `alpha / 4 / log(n) ** 2`.

    Raises
    ------
    NetworkXNotImplemented
        If the input graph is not undirected

    See Also
    --------
    :meth: `sparse_cut`
    :meth: `sparsest_cut`
    """
    S = set()
    H = G
    while len(S) < balance * len(G):
        A, B = sparse_cut(H, alpha, _s, _t, **kwargs)
        # swap A and B if A is bigger
        if len(B) < len(A):
            temp = A
            A = B
            B = temp
        # if no cut could be found, then return early
        if not A:
            return set(), set(G.nodes())

        S = S.union(A)
        H = G.subgraph(B)
    return S, set(G).difference(S)
