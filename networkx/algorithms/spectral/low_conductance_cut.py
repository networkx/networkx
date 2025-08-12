"""
Implementation of the RST cut matching algorithm for finding a cut of low conductance.
"""

import math

import numpy as np
import scipy as sp

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
    flow_func,
    **kwargs,
):
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
    T = math.ceil(t_const + t_slope * math.log(m) ** 2)
    c = math.ceil(1 / alpha / math.log(m) ** 2)

    # map of nodes to indices. Note that the first n indices will be
    # nodes of G, then the remainder will be subdivision nodes.
    vertex_to_index = {v: i for i, v in enumerate(subdivision_graph)}

    proj_flow_vectors = generate_random_orthogonal_gaussian(m, num_candidates)

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
        for v in active_subdiv_nodes:
            if proj_flow_vector[vertex_to_index[v] - n] < proj_avg_flow:
                L.append(v)
            else:
                R.append(v)
            if len(L) > len(R):
                temp = L
                L = R
                R = temp
        return (L, R)

    def propose_cut(proj_flow_vector, strategy):
        num_active = len(active_subdiv_nodes)
        # compute average projected flow
        proj_avg_flow = average_flow(proj_flow_vector).item()

        L, R = initial_partition(proj_flow_vector, proj_avg_flow)
        # compute potentials
        total_potential = compute_potential(
            active_subdiv_nodes, proj_flow_vector, proj_avg_flow
        ).item()
        left_potential = compute_potential(L, proj_flow_vector, proj_avg_flow).item()

        if left_potential >= total_potential / 20:
            # sort L by flow
            L.sort(key=lambda v: proj_flow_vector[vertex_to_index[v] - n])
            if strategy == "unbalanced":
                while len(L) > num_active // 8:
                    L.pop()
            elif strategy == "balanced":
                # remove arbitrary vertices, as there is no requirement on R.
                # TODO: might by better if you sort and remove largest
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
                L.sort(
                    key=lambda v: proj_flow_vector[vertex_to_index[v] - n], reverse=True
                )
                while len(L) > num_active // 8:
                    L.pop()
            elif strategy == "balanced":
                while len(R) > len(L):
                    R.pop()
        return (set(L), set(R))

    for i in range(max(T, min_iterations)):
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
        if potentials[best_potential_index] < 1 / 16 / num_active**3:
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
            H = subdivision_graph.subgraph(S)
            active_subdiv_nodes.difference_update(C)
            if len(C) > max(m / 10 / T, m * b):
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
        )
        # zero out the 1's on the diagonal of matched vertices
        W += sp.sparse.coo_array(
            ([-1] * len(matching_rows), (matching_rows, matching_rows)), (m, m)
        ).tocsr()
        proj_flow_vectors = W @ proj_flow_vectors
    return C.intersection(set(G)), set(G).difference(C)


@not_implemented_for("directed")
@nx._dispatchable
def lowest_conductance_cut(
    G,
    alpha,
    _s,
    _t,
    min_iterations=0,
    num_candidates=20,
    b=0.0,
    t_const=20,
    t_slope=5,
    subdiv_node_format=None,
    strategy="balanced",
    flow_func=None,
    **kwargs,
):
    if len(G.edges()) < 2:
        raise nx.NetworkXError("G must have at least 2 edges.")

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
        raise nx.NetworkXError("Balance parameters b must be between 0 and 1.")

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
        flow_func,
        **kwargs,
    )
