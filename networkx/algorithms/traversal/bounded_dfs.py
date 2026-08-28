"""Bounded-Scope Depth-First Search (BS-DFS) for length-bounded simple path and cycle enumeration."""


# Implementation overview
# -----------------------
# An iterative depth-limited depth-first search starting at ``s``.
# To prevent excessive fruitless searches, the search is pruned by node barriers.
#
# Barriers
# --------
# The search maintains one integer per node, ``b[v]``, a *certified lower bound*
# on the number of edges from ``v`` to ``t*`` in the graph minus the nodes
# currently on the search stack ``stack``.  All barriers start at 0, which is
# trivially valid.  With ``v`` on top of ``stack`` at depth ``h`` (so ``h`` edges
# from ``s`` to ``v``), a successor ``w`` is *admissible* iff
#
#     b[w] + h < k                                                        (A)
#
# Rationale: entering ``w`` costs one edge, and ``b[w]`` further edges are needed
# before ``t*`` can possibly be reached, so any output through ``w`` has length
# at least ``h + 1 + b[w]``; requiring that to be at most ``k`` is exactly (A).
# Because ``b[w]`` is a *lower* bound, (A) never discards an output: it prunes
# only branches that provably cannot finish within the budget.
#
# Barriers are written in exactly two places, both when the search at ``v``
# finishes with ``v`` at depth ``h``:
#
# * **unfruitful** -- the search at ``v`` produced no output.  The subsearch had a
#   budget of ``k - h`` edges and exhausted it, so ``t*`` is farther than that:
#
#       b[v] = k - h + 1                                    (a *raise*)
#
# * **fruitful** -- the search at ``v`` produced an output, and ``sd`` is the exact
#   number of edges from ``v`` to ``t*`` along the shortest output found below
#   ``v``.  Setting ``b[v] = sd`` may *invalidate* the barriers of predecessors,
#   which were justified relative to a larger distance from ``v``.  A backward
#   BFS restores the invariant
#
#       b[u] <= b[w] + 1     for every edge u -> w with u not on stack       (EC)
#
#   ("edge-consistency"), lowering barriers where needed; see ``cascade`` below.
#   Nodes on ``stack`` are skipped: their barriers are written when they are popped,
#   not while they are forbidden.
#
# Edge-consistency is what makes the pop obligation local, and it is why the
# cascade terminates quickly: a node is re-entered by the BFS only when its
# barrier strictly drops, and each barrier only ever moves within ``[0, k+1]``.
#
# Delay
# -----
# Every cascade is triggered by a fruitful search, i.e. it is charged to an
# output that has already been emitted.  Together with the raise bound this
# gives worst-case delay ``3(k+1)(n+m)`` and amortized delay ``2(k+1)(n+m)``,
# with ``n`` nodes and ``m`` edges -- in particular ``O(k(n+m))`` with a small
# constant.  See [1]_.
#
# Prior work
# ----------
# Two earlier algorithms for the same enumeration problems are listed here as
# prior art, not as alternatives: [1]_ and [2]_ demonstrate inputs on which
# [3]_ and [4]_ omit valid outputs.
#
# References
# ----------
# .. [1] Frank Bauernoeppel, Joerg-Ruediger Sack,
#     "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
#     with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers", 2026,
#     https://arxiv.org/abs/2607.14745
# .. [2] Frank Bauernoeppel, Joerg-Ruediger Sack,
#     "Finding All Bounded-Length Simple Cycles in a Directed Graph --
#     Revisited", 2025, https://arxiv.org/abs/2512.08392
# .. [3] Y. Peng et al., "Efficient Hop-constrained s-t Simple Path
#     Enumeration", The VLDB Journal 30(5):799-823, 2021,
#     https://doi.org/10.1007/s00778-021-00674-5
# .. [4] A. Gupta and T. Suzumura, "Finding All Bounded-Length Simple Cycles
#     in a Directed Graph", 2021, https://arxiv.org/abs/2105.10094

import itertools
from collections import defaultdict, deque

import networkx as nx

__all__ = ["bsdfs", "bsdfs_edges"]


_NO_TARGET = object()  # sentinel: never equal to any node
_INF = float("inf")  # sentinel shortest distance: no target found below


@nx._dispatchable
def bsdfs(G, s, t, k):
    """Yield all length-bounded simple paths or cycles from ``s`` to ``t``.

    Parameters
    ----------
    G : NetworkX graph
        Directed or undirected, graph or multigraph.
    s : node
        Source node, where every reported walk starts.
    t : node or set of nodes
        A single node enumerates the simple paths from ``s`` to ``t``; as a
        special case, ``t == s`` enumerates the simple cycles through ``s``.
        A set enumerates the simple paths from ``s`` to any node of the set,
        and such a path may pass through one node of the set on its way to
        another.  A single node and the corresponding one-element set give
        the same paths, except in the cycle case ``t == s``.
    k : int
        Length bound in edges.

    Yields
    ------
    list of nodes
        The nodes of the walk, beginning at ``s`` and ending at the target
        reached.  All nodes are distinct, except that a cycle (``t == s``)
        ends at ``s`` again.  The one-node list ``[s]`` is yielded for the
        trivial path, i.e. when ``s`` is itself a target.

    Raises
    ------
    ValueError
        If ``k`` is negative, or ``t`` is an empty set.
    NodeNotFound
        If ``s`` is not in ``G``, or ``t`` is neither a node of ``G`` nor a
        set of nodes.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])

    With ``t == s`` these are the cycles through ``s``, ending at ``s``
    again.  The 4-edge cycle 0, 1, 2, 3 exceeds the bound.

    >>> list(bsdfs(G, 0, 0, 3))
    [[0, 1, 3, 0], [0, 2, 3, 0]]

    Cycles through the edge (0, 1) are the paths from 1 back to 0, with one
    edge of the bound already spent by that edge.

    >>> list(bsdfs(G, 1, 0, 2))
    [[1, 3, 0]]

    A set of targets may be passed through, so 0, 1, 2, 3 is reported
    although it runs through the target 2.  A single node and the matching
    one-element set agree.

    >>> list(bsdfs(G, 0, {2, 3}, 3))
    [[0, 1, 2], [0, 1, 2, 3], [0, 1, 3], [0, 2], [0, 2, 3]]
    >>> list(bsdfs(G, 0, {3}, 3)) == list(bsdfs(G, 0, 3, 3))
    True

    ``s`` in a target set yields the trivial path ``[s]`` and nothing more,
    since no simple path returns to ``s``; ``t == s`` is the cycle query.

    >>> list(bsdfs(G, 0, {0, 3}, 3))
    [[0], [0, 1, 2, 3], [0, 1, 3], [0, 2, 3]]

    See Also
    --------
    :func:`bsdfs_edges`
    :func:`~networkx.algorithms.simple_paths.all_simple_paths`
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths`
    :func:`~networkx.algorithms.cycles.simple_cycles`

    Notes
    -----
    Between consecutive outputs the algorithm performs at most
    ``3(k+1)(n+m)`` elementary steps on a graph with ``n`` nodes and ``m``
    edges, and at most ``2(k+1)(n+m)`` amortized over all outputs [1]_.
    One elementary step is a single adjacency-list entry scanned, plus
    constant bookkeeping per call and per barrier update, so the delay is
    ``O(k(n+m))``.

    A search from several sources is obtained by adding a virtual source node
    joined to each of them, running with the bound ``k + 1``, and dropping the
    leading virtual edge from each result.  The sources do not block one
    another, so a walk from one may pass through another.

    References
    ----------
    .. [1] Frank Bauernoeppel, Joerg-Ruediger Sack,
        "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
        with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers", 2026,
        https://arxiv.org/abs/2607.14745
    """

    if k < 0:
        raise ValueError(f"length bound {k=} must be non-negative")
    if s not in G:
        raise nx.NodeNotFound(f"source node {s} not in graph")

    if t in G:  # a single node: terminal, exactly as in the paper
        terminal, targets = t, frozenset()
    else:  # a set of nodes: NetworkX extension, targets are entered
        try:
            targets = set(t)
        except TypeError as err:
            raise nx.NodeNotFound(
                f"target {t!r} is neither a node of G nor an iterable of nodes"
            ) from err
        if not targets:
            raise ValueError(f"{t=} must be a node or a non-empty set of nodes")
        terminal = _NO_TARGET

    G_succ = G._succ if G.is_directed() else G._adj
    G_pred = G._pred if G.is_directed() else G._adj

    barrier = defaultdict(int)  # barriers, persistent over the whole run
    stack = [s]  # search path, node stack
    forbidden = {s}  # nodes on the stack in a set, forbidden for re-visiting
    iters = [iter(G_succ[s])]  # one successor iterator per frame
    shortest_distances = [_INF]  # per frame: shortest distance to a target

    if s in targets:  # the source is itself a target
        shortest_distances[-1] = 0
        yield [s]

    def cascade(v, sd):
        """Fruitful write ``b[v] = sd``, then restore (EC) by backward BFS."""
        barrier[v] = sd
        queue = deque([(v, sd)])
        while queue:
            w, d = queue.popleft()
            for u in G_pred[w]:
                if u not in forbidden and barrier[u] > d + 1:
                    barrier[u] = d + 1  # (EC) was violated at u -> w
                    queue.append((u, d + 1))

    while iters:
        h = len(stack) - 1  # depth of the top node v
        for w in iters[-1]:
            if barrier[w] + h < k:  # admissible
                if w == terminal:  # terminal target: report, do not enter
                    yield stack + [w]
                    if shortest_distances[-1] > 1:
                        shortest_distances[-1] = 1
                elif w not in forbidden:
                    stack.append(w)
                    forbidden.add(w)
                    iters.append(iter(G_succ[w]))
                    if w in targets:  # a target: report the path on arrival
                        shortest_distances.append(0)
                        yield stack[:]
                    else:
                        shortest_distances.append(_INF)
                    break  # descend search to w
        else:  # all descend searches completed, finish search at v
            v = stack[-1]
            iters.pop()
            sd = shortest_distances.pop()
            if sd <= k:
                cascade(v, sd)  # fruitful; v still forbidden
            else:
                barrier[v] = k - h + 1  # unfruitful raise
            stack.pop()
            forbidden.discard(v)
            if shortest_distances and sd + 1 < shortest_distances[-1]:
                shortest_distances[-1] = sd + 1  # propagate distance to caller


@nx._dispatchable
def bsdfs_edges(G, s, t, k):
    """Yield the walks of :func:`bsdfs` as edge lists rather than node lists.

    This is to :func:`bsdfs` what
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths` is to
    :func:`~networkx.algorithms.simple_paths.all_simple_paths`.  The search
    is identical; only the reporting differs.  On a multigraph one node walk
    corresponds to several edge walks, one per combination of parallel edge
    keys, and all of them are yielded.

    Parameters
    ----------
    G : NetworkX graph
        Directed or undirected, graph or multigraph.
    s : node
        Source node, where every reported walk starts.
    t : node or set of nodes
        A single node enumerates the simple paths from ``s`` to ``t``; as a
        special case, ``t == s`` enumerates the simple cycles through ``s``.
        A set enumerates the simple paths from ``s`` to any node of the set,
        and such a path may pass through one node of the set on its way to
        another.  A single node and the corresponding one-element set give
        the same paths, except in the cycle case ``t == s``.
    k : int
        Length bound in edges.

    Yields
    ------
    list of edges
        The edges of the walk, as ``(u, v)``, resp. ``(u, v, key)`` on a
        multigraph.  The empty list is yielded for the trivial path, i.e.
        when ``s`` is itself a target.

    Raises
    ------
    ValueError
        If ``k`` is negative, or ``t`` is an empty set.
    NodeNotFound
        If ``s`` is not in ``G``, or ``t`` is neither a node of ``G`` nor a
        set of nodes.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])
    >>> list(bsdfs_edges(G, 0, 3, 3))
    [[(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2), (2, 3)]]

    Parallel edges give one walk each, distinguished by their key.

    >>> M = nx.MultiDiGraph([(0, 1), (0, 1), (1, 2)])
    >>> list(bsdfs(M, 0, 2, 3))
    [[0, 1, 2]]
    >>> list(bsdfs_edges(M, 0, 2, 3))
    [[(0, 1, 0), (1, 2, 0)], [(0, 1, 1), (1, 2, 0)]]

    See Also
    --------
    :func:`bsdfs`
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths`
    """
    walks = bsdfs(G, s, t, k)
    if G.is_multigraph():
        for walk in walks:
            choices = [[(u, v, key) for key in G[u][v]] for u, v in zip(walk, walk[1:])]
            yield from (list(c) for c in itertools.product(*choices))
    else:
        for walk in walks:
            yield [(u, v) for u, v in zip(walk, walk[1:])]
