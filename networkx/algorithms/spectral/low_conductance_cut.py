"""
Implementation of the RST cut matching algorithm for finding a cut of low conductance.
"""

import math

import networkx as nx
from networkx.utils.decorators import not_implemented_for

from .utils import (
    build_flow_network,
    build_subdivision_graph,
    compute_mincut,
    flow_matching,
    generate_random_orthogonal_gaussian,
)

__all__ = ["lowest_conductance_cut"]


def lowest_conductance_cut_impl(
    G,
    alpha,
    _s,
    _t,
    min_iterations,
    num_candidates,
    b,
    t_const,
    t_slope,
    subdiv_node_format,
    strategy,
    fast_randomization,
    flow_func,
    _seed,
    **kwargs,
):
    import numpy as np
    import scipy as sp

    n = len(G)
    m = len(G.edges())
    subdivision_graph, active_subdiv_nodes = build_subdivision_graph(
        G, subdiv_node_format=subdiv_node_format
    )
    # H will contain a subgraph view of the subdivision_graph. To avoid nested views, it's necessary
    # to store H and the subdivision graph separately.
    H = subdivision_graph
    # The cut so far. Denoted R in SW'21
    C = set()
    cut_volume = 0
    T = math.ceil(t_const + t_slope * math.log(m) ** 2)
    c = math.ceil(1 / alpha / (math.log(m) ** 2 + 0.01))

    # map of nodes to indices. Note that the first n indices will be
    # nodes of G, then the remainder will be subdivision nodes.
    vertex_to_index = {v: i for i, v in enumerate(subdivision_graph)}

    if fast_randomization:
        matching_graphs = [sp.sparse.identity(m)]

    proj_flow_vectors = generate_random_orthogonal_gaussian(
        m, num_candidates, _seed=_seed
    )

    def compute_potential(S, vecs, proj_avg_flow, exp=2):
        bit_mask = [False] * m
        for v in S:
            bit_mask[vertex_to_index[v] - n] = True
        compatible_shape = (m, 1)
        if len(vecs.shape) == 1:
            compatible_shape = (m,)
        bit_mask = np.array(bit_mask).reshape(compatible_shape)
        return np.sum(np.abs(vecs - proj_avg_flow) ** exp, axis=0, where=bit_mask)

    def average_flow(vecs):
        bit_mask = [False] * m
        for v in active_subdiv_nodes:
            bit_mask[vertex_to_index[v] - n] = True
        # Need to do this check, otherwise the method will not work for both
        # 1d vectors and arrays.
        compatible_shape = (m, 1)
        if len(vecs.shape) == 1:
            compatible_shape = (m,)
        bit_mask = np.array(bit_mask).reshape(compatible_shape)
        return np.mean(vecs, axis=0, where=bit_mask)

    def initial_partition(proj_flow_vector, proj_avg_flow):
        L = []
        R = []
        should_reverse = False
        for v in active_subdiv_nodes:
            if proj_flow_vector[vertex_to_index[v] - n] < proj_avg_flow:
                L.append(v)
            else:
                R.append(v)
            if len(L) > len(R):
                temp = L
                L = R
                R = temp
                should_reverse = True
        return L, R, should_reverse

    def propose_cut(proj_flow_vector, strategy):
        num_active = len(active_subdiv_nodes)
        # compute average projected flow
        proj_avg_flow = average_flow(proj_flow_vector).item()

        L, R, should_reverse = initial_partition(proj_flow_vector, proj_avg_flow)
        # compute potentials
        total_potential = compute_potential(
            active_subdiv_nodes, proj_flow_vector, proj_avg_flow
        ).item()
        left_potential = compute_potential(L, proj_flow_vector, proj_avg_flow).item()
        if left_potential >= total_potential / 20:
            # sort L by flow
            L.sort(
                key=lambda v: proj_flow_vector[vertex_to_index[v] - n],
                reverse=should_reverse,
            )
            if strategy == "unbalanced":
                while len(L) > num_active // 8:
                    L.pop()
            elif strategy == "balanced":
                # remove arbitrary vertices, as there is no requirement on R.
                while len(R) > len(L):
                    R.pop()
            return (set(L), set(R))

        left_l1_potential = compute_potential(L, proj_flow_vector, proj_avg_flow, exp=1)
        # repartition with new cutoff
        L.clear()
        R.clear()
        for v in active_subdiv_nodes:
            if (
                proj_flow_vector[vertex_to_index[v] - n]
                <= proj_avg_flow + 4 / num_active * left_l1_potential
            ):
                R.append(v)
            elif (
                proj_flow_vector[vertex_to_index[v] - n]
                >= proj_avg_flow + 6 / num_active * left_l1_potential
            ):
                L.append(v)
            # sort R by flow and prune
        if strategy == "unbalanced":
            L.sort(key=lambda v: proj_flow_vector[vertex_to_index[v] - n], reverse=True)
            while len(L) > num_active // 8:
                L.pop()
        elif strategy == "balanced":
            while len(R) > len(L):
                R.pop()
        return (set(L), set(R))

    for _ in range(max(T, min_iterations)):
        # get best candidate among random gaussians
        num_active = len(active_subdiv_nodes)
        proj_avg_flow = average_flow(proj_flow_vectors)
        potentials = compute_potential(
            active_subdiv_nodes, proj_flow_vectors, proj_avg_flow
        )
        best_potential_index = np.argmax(potentials)
        u = proj_flow_vectors[:, best_potential_index]

        # Projected potential is an unbiased estimator of the actual potential. So
        # we either have a near-expander or an expander and can stop early.
        # See GPG'24 Practical Expander Decomposition
        if potentials[best_potential_index] < 1 / 64 / num_active**3:
            return C.intersection(set(G)), set(G).difference(C)

        # get cut from best vector
        A, B = propose_cut(u, strategy)

        # build flow network using H and A, B
        F = build_flow_network(H, _s, _t, A, B, c, 1)

        # solve flow
        R = flow_func(F, _s, _t, **kwargs)
        if R.graph["flow_value"] < min(len(A), len(B)):
            # Flow was not routable. Compute a cut and remove the cut
            # from the set of active subdiv nodes.
            Q, S = compute_mincut(R, _t)
            C.update(Q)
            cut_volume += sum(
                subdivision_graph.degree[v] for v in Q if v not in {_s, _t}
            )
            H = subdivision_graph.subgraph(S)
            active_subdiv_nodes.difference_update(C)
            if cut_volume > max(m / 10 / T, 4 * b * m):
                return C.intersection(set(G)), set(G).difference(C)

        # get matching from flow
        matching = flow_matching(R, _s, _t)
        matching_rows = [vertex_to_index[i] - n for i in matching]
        matching_cols = [vertex_to_index[i] - n for i in matching.values()]

        # Average across matching edges
        W = (
            sp.sparse.identity(m)
            + sp.sparse.coo_array(
                ([0.5] * len(matching_rows), (matching_rows, matching_cols)), (m, m)
            ).tocsr()
            - sp.sparse.coo_array(
                ([0.5] * len(matching_rows), (matching_rows, matching_rows)), (m, m)
            ).tocsr()
        )
        if fast_randomization:
            # This is quite a significant divergence from Arvestad's implementation.
            # I found that resampling the flow vectors every time improved the running
            # time quite drastically, especially for the unbalanced strategy. This makes
            # the theoretical complexity O(log(m)^3 ...), and increases slightly the
            # space requirements to O(n * log(m)^2)
            matching_graphs.append(W)
            proj_flow_vectors = generate_random_orthogonal_gaussian(
                m, num_candidates, _seed=_seed
            )
            for M in matching_graphs:
                proj_flow_vectors = M @ proj_flow_vectors
        else:
            proj_flow_vectors = W @ proj_flow_vectors

    return C.intersection(set(G)), set(G).difference(C)


@not_implemented_for("directed")
def lowest_conductance_cut(
    G,
    alpha,
    _s,
    _t,
    min_iterations=0,
    num_candidates=20,
    b=0.45,
    t_const=22.0,
    t_slope=5.0,
    subdiv_node_format=None,
    strategy="balanced",
    fast_randomization=True,
    flow_func=None,
    _seed=None,
    **kwargs,
):
    r"""With high probability, given a graph `G` with m edges and a parameter `alpha`
    either finds a cut with balance at least $1 - 1 / 10 \log(m)^2$ and conductance
    at most $\alpha \log(m)^2$, or certifies that `G` has conductance about
    `alpha` / `t_slope`, or finds an unbalanced cut such that the remaining nodes
    form about a nearly `alpha / t_slope` expander in `G`.

    If no cut is found, the actual conductance guarantee is that `G` has
    conductance at least `alpha * log(m) ** 2 / (t_const + t_slope * log(m) ** 2)`,
    and the same guarantee if the algorithm finds an unbalanced cut.

    This algorithm runs in time $O(\log^2(m) (T_f + m / \alpha \log(m))))$.
    where $T_f$ is the time taken by a single run of `flow_func`.

    Parameters
    ----------
    G : NetworkX Graph or Multigraph

    alpha : float
        The conductance parameter.

    _s : object
        A key for a super-source node added during flow computations in the algorithm.
        It must satisfy `_s not in G`.

    _t : object
        A key for a super-sink node added during flow computations. It must satisfy
        `_t not in G`.

    min_iterations : int
        A minimum number of iterations to run before the algorithm returns an
        unbalanced cut. The algorithm may run for fewer iterations if it has found
        a balanced cut or a certificate that `G` has high conductance.

    num_candidates : int
        The number of random unit vectors to consider during the course of the
        algorithm. Higher values slow down computations slightly, but improve
        the quality of cuts found and improve confidence in conductance
        guarantees.

    b : float
        A balance parameter for cuts. The algorithm will attempt to find a cut
        of balance `max(b, 1 - 1 / log(m) ** 2)`. Note that finding such a
        balanced cut is not guaranteed, and it may return cuts of balance
        between `1 - 1 / log(m) ** 2` and `b`.

    t_const : float
        The algorithm will run for at most `t_const + t_slope * log(m) ** 2`
        iterations. See [2]_ for experiments on the best value to use here.

    t_slope : float
        see `t_const`.

    subdiv_node_format : function
        A function taking in two nodes u, v and returning a key for the
        subdivision node of the edge (u, v). It should satisfy
        `subdiv_node_format(u, v) not in G` for each edge (u, v). Defaults
        to `lambda u, v : f"{str(u)} - {str(v)}` if not specified.

    strategy : str
        The strategy to be used in the cut finding step. Supported values
        are "balanced" or "unbalanced".

    fast_randomization : bool
        Whether or not to resample the projected flow vectors on each iteration.
        This adds O(n * log(m) ** 3) to the theoretical running time but usually
        decreses actual running time, especially for the unbalanced strategy.

    flow_func : function
        A function for computing the maximum flow among a pair of nodes
        in a capacitated graph. The function has to accept at least three
        parameters: a Graph or Digraph, a source node, and a target node.
        And return a residual network that follows NetworkX conventions
        (see Notes). If flow_func is None, the default maximum
        flow function (:meth:`preflow_push`) is used. The choice of the default
        function may change from version to version and should not be relied on.

    _seed : integer, random_state, or None (default)
        Indicator of random number generation state.
        See :ref:`Randomness<randomness>`.

    kwargs : Any other keyword parameter is passed to the function that
        computes the maximum flow.

    Returns
    -------
    tuple(Set, Set)
        A cut in the graph `G` which is either balanced and has conductance at
        most `alpha * log(m) ** 2`, or unbalanced such that the larger side of
        the cut is a nearly `alpha` expander in `G`. In particular, if the smaller
        side of the cut is empty, then `G` has conductance at least `alpha`. The
        smaller side will always be returned first.

    Raises
    ------
    NetworkXError
        If `G` has less than 2 edges, if `_s in G or _t in G`.

    NetworkXNotImplemented
        If the input graph is not undirected.

    Notes
    -----
    This algorithm follows the implementation in [2]_ with some slight
    modifications. In [2]_, the flow function used is a modifed variant
    of preflow-push called UnitFlow. [2]_ also found that in practice, preflow
    push is more efficient than the UnitFlow algorithm, despite UnitFlow
    having better theoretical complexity. Many details regarding the algorithm
    as well as choices of parameters can be found in [3]_.

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
    .. [1] T. Sarunarak, and D. Wang. Expander Decomposition and Pruning:
            Faster, Stronger, and Simpler. J. SODA, 30:2616-2635, 2019.

    .. [2] L. Gottesburn, N. Parotsidis, and M. P. Gutenburg. Practical
            Expander Decomposition. J. ESA, 32(61):1-17, 2024.

    .. [3] Isaac Arvestad. Near-linear Time Expander Decomposition in Practice.
            Master's thesis, KTH Royal Institute of Technology, 2022.
    """
    if len(G.edges()) == 0:
        return set(), set(G)

    if flow_func is None:
        if kwargs:
            raise nx.NetworkXError(
                "You have to explicitly set a flow_func if"
                " you need to pass parameters via kwargs."
            )
        flow_func = nx.algorithms.flow.preflow_push
    if not callable(flow_func):
        raise nx.NetworkXError("flow_func must be callable.")

    if subdiv_node_format and not callable(subdiv_node_format):
        raise nx.NetworkXError("subdiv_node_format must be callable.")

    if _s == _t:
        raise nx.NetworkXError("super-source node is the same as super-sink node.")

    if strategy not in {"balanced", "unbalanced"}:
        raise nx.NetworkXError("Strategy must be either 'balanced' or 'unbalanced'.")

    if t_slope <= 0:
        raise nx.NetworkXError(
            "The algorithm runs for t_const + t_slope * log(m)^2 iterations. t_slope must be positive."
        )
    if t_const + t_slope * math.log(len(G.edges())) ** 2 < 0:
        raise nx.NetworkXError(
            "The algorithm runs for t_const + t_slope * log(m)^2 < 0 iterations. "
            "Tune your values of t_const and t_slope so that this is positive."
        )

    if b < 0 or b > 1:
        raise nx.NetworkXError("Balance parameter b must be between 0 and 1.")

    return lowest_conductance_cut_impl(
        G,
        alpha,
        _s,
        _t,
        min_iterations,
        num_candidates,
        b,
        t_const,
        t_slope,
        subdiv_node_format,
        strategy,
        fast_randomization,
        flow_func,
        _seed,
        **kwargs,
    )
