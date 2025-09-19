"""
Implementation of the Saranurak Wang expander decomposition algorithm.
"""

import math

import networkx as nx
from networkx import set_edge_attributes
from networkx.algorithms.flow import preflow_push
from networkx.algorithms.spectral.low_conductance_cut import lowest_conductance_cut
from networkx.utils.decorators import not_implemented_for

from .utils import compute_mincut

__all__ = ["expander_decomposition"]


def max_flow_trimming(G, A, alpha, _s, _t, flow_func=None, **kwargs):
    """Given a graph `G`, a conductance parameter `alpha, and a subset `A`
    which is a nearly `alpha` expander in G, find a subset `S`, such that
    the induced graph on `A - S` is an `alpha / 6` expander.

    Parameters
    ----------
    G : NetworkX Graph

    A : collection
        A collection of nodes in `G` such that `A` is a nearly `alpha`
        expander in `G`.

    alpha : float
        A conductance parameter. The returned set `S` will be such that
        the induced graph on `A - S` is an `alpha / 6` expander

    _s : object
        A key for a super-source node added during flow computations. Must
        satisfy `_s not in G`.

    _t : object
        A key for a super-sink node added during flow computations. Must
        satisfy `_t not in G`.

    flow_func : function

    kwargs : Any keyword arguments to be passed to the flow function

    """
    if flow_func is None:
        flow_func = preflow_push
        if kwargs:
            raise nx.NetworkXError(
                "Must specify flow function if you want to pass in kwargs."
            )

    # Set up the flow problem
    total_flow = 0
    H = G.subgraph(A).copy()  # TODO: Is this too slow?
    set_edge_attributes(H, 2 / alpha, "capacity")
    H.add_node(_s)
    H.add_node(_t)
    for u in H:
        supply = G.degree(u) - H.degree(u)
        total_flow += supply
        H.add_edge(_s, u, capacity=supply)
        H.add_edge(u, _t, capacity=H.degree(u))

    # solve the flow
    R = preflow_push(H, _s, _t, **kwargs)
    if R.graph["flow_value"] < total_flow:
        return compute_mincut(R, _t)
    return set(), set(G)


@not_implemented_for("directed")
def expander_decomposition(
    G, alpha, _s, _t, max_flow_trimming=True, trimming_kwargs=None, **kwargs
):
    r"""Given a graph `G` with `n` nodes and `m` edges, and a conductance parameter
    `alpha`, finds with high probability a partition such that each cluster is
    a `6 * alpha` expander and the total number of intercluster edges is
    $O(\alpha m \log(m)^3)$

    This algorithm runs in time $O(\log(m)^4(m / \alpha + T_f))$ where $T_f$ is the
    time it takes to compute a single commodity max flow.

    Parameters
    ----------
    G : NetworkX Graph

    alpha : float
        A conductance parameter such that each returned cluster is an `alpha`
        expander.

    _s : object
        A key for a super-source node added during flow computations. Must satisfy
        `_s not in G`.

    _t : object
        A key for a super-sink node added during flow computations. Must satisfy
        `_t not in G`.

    max_flow_trimming : bool
        Whether to use exact max flow or approximate max flow for trimming. Currently
        only exact max flow trimming is supported. This is also usually faster.

    trimming_kwargs : dict
        A dictionary of keyword arguments to be passed to the trimming function

    kwargs : Any keyword argument to be passed to the lowest_conductance_cut function.
            This includes a _seed argument to control the RNG.

    Returns
    -------
    list[set]
        A list of disjoint clusters which partition `G`, such that the induced
        subgraph of each cluster is an `alpha` expander, and the number of
        intercluster edges is $O(\alpha m \log(m)^3)$.

    Raises
    ------
    NetworkXNotImplemented
        If the input graph is not undirected, or max_flow_trimming is False.

    See Also
    --------
    :meth: `lowest_conductance_cut`

    References
    ----------
    .. [1] T. Sarunarak, and D. Wang. Expander Decomposition and Pruning:
            Faster, Stronger, and Simpler. J. SODA, 30:2616-2635, 2019.

    .. [2] L. Gottesburn, N. Parotsidis, and M. P. Gutenburg. Practical
            Expander Decomposition. J. ESA, 32(61):1-17, 2024.

    .. [3] Isaac Arvestad. Near-linear Time Expander Decomposition in Practice.
            Master's thesis, KTH Royal Institute of Technology, 2022.
    """
    if max_flow_trimming:
        trimming_func = max_flow_trimming
    else:
        raise nx.NetworkXNotImplemented(
            "Near linear time trimming is not supported yet."
        )

    def expander_decomposition_impl(H, alpha, _s, _t, **kwargs):
        m = len(H.edges())
        S, T = lowest_conductance_cut(H, 6 * alpha, _s, _t, **kwargs)
        if len(S) == 0:
            # certified that G is an 6 * alpha expander, return set(G).
            return [T]

        elif nx.volume(H, S) > m / 10 / math.log(m) ** 2:
            # balanced cut, recurse on each side separately
            left_side = G.subgraph(S)
            right_side = G.subgraph(T)
            return expander_decomposition_impl(
                left_side, alpha, _s, _t, **kwargs
            ) + expander_decomposition_impl(right_side, alpha, _s, _t, **kwargs)

        else:
            # unbalanced cut gives near expander. Trim and recurse on one
            # side only.
            trimmed, expander = trimming_func(G, T, alpha, _s, _t, **trimming_kwargs)
            trimmed = trimmed.union(S)
            return [expander] + expander_decomposition_impl(
                G.subgraph(trimmed), alpha, _s, _t, **kwargs
            )

    return expander_decomposition_impl(G, alpha, _s, _t, **kwargs)
