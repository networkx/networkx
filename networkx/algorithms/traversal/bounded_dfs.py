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
# Barriers are written in exactly two places, both on return from ``Search(v)``
# with ``v`` at depth ``h``:
#
# * **unfruitful return** -- ``v`` produced no output.  The subsearch had a
#   budget of ``k - h`` edges and exhausted it, so ``t*`` is farther than that:
#
#       b[v] = k - h + 1                                    (a *raise*)
#
# * **fruitful return** -- ``v`` produced an output, and ``sd`` is the exact
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
# Every cascade is triggered by a fruitful return, i.e. it is charged to an
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

from collections import defaultdict, deque

import networkx as nx

__all__ = ["bsdfs"]


_NO_TARGET = object()  # sentinel: never equal to any node
_INF = float("inf")  # sentinel shortest distance: no target found below


class _OutEdgeCache(dict):
    """Caches, per node, the list of its outgoing edges as tuples."""

    def __init__(self, G):
        self.G = G
        self.keys_ = G.is_multigraph()

    def __missing__(self, v):
        G = self.G
        out = self[v] = list(G.edges(v, keys=True) if self.keys_ else G.edges(v))
        return out


class _InNodeCache(dict):
    """Caches, per node, the list of its predecessors.  The cascade direction."""

    def __init__(self, adj):
        self.adj = adj

    def __missing__(self, v):
        out = self[v] = list(self.adj[v])
        return out


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
    list of edges
        The edges of the walk from ``s``, as ``(u, v)`` resp. ``(u, v, key)``.
        Empty only for the trivial path, i.e. when ``s`` is itself a target.

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

    With ``t == s`` these are the cycles through ``s``; the 4-edge cycle
    0, 1, 2, 3 exceeds the bound.  A caller wanting nodes drops the last
    component of each edge.

    >>> list(bsdfs(G, 0, 0, 3))
    [[(0, 1), (1, 3), (3, 0)], [(0, 2), (2, 3), (3, 0)]]
    >>> [[e[0] for e in E] for E in bsdfs(G, 0, 0, 3)]
    [[0, 1, 3], [0, 2, 3]]

    Cycles through the edge (0, 1): search from 1 back to 0, with one edge of
    the bound already spent, and prepend 0.

    >>> [[0] + [e[0] for e in E] for E in bsdfs(G, 1, 0, 2)]
    [[0, 1, 3]]

    A set of targets may be passed through, so 0, 1, 2, 3 is reported
    although it runs through the target 2.  A single node and the matching
    one-element set agree.

    >>> list(bsdfs(G, 0, {2, 3}, 3))
    [[(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2)], [(0, 2), (2, 3)]]
    >>> list(bsdfs(G, 0, {3}, 3)) == list(bsdfs(G, 0, 3, 3))
    True

    ``s`` in a target set yields the trivial path and nothing more, since no
    simple path returns to ``s``; ``t == s`` is the cycle query instead.

    >>> list(bsdfs(G, 0, {0, 3}, 3))
    [[], [(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2), (2, 3)]]

    See Also
    --------
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths`
    :func:`~networkx.algorithms.simple_paths.all_simple_paths`
    :func:`~networkx.algorithms.cycles.simple_cycles`

    Notes
    -----
    Between consecutive outputs the algorithm performs at most
    ``3(k+1)(n+m)`` elementary steps on a graph with ``n`` nodes and ``m``
    edges, and at most ``2(k+1)(n+m)`` amortized over all outputs [1]_.
    One elementary step is a single adjacency-list entry scanned, plus
    constant bookkeeping per call and per barrier update, so the delay is
    ``O(k(n+m))``.

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
            raise nx.NodeNotFound(f"target node {t} not in graph") from err
        if not targets:
            raise ValueError(f"{t=} must be a node or a non-empty set of nodes")
        terminal = _NO_TARGET

    succ = _OutEdgeCache(G)
    pred = _InNodeCache(G.pred if G.is_directed() else G.adj)

    barrier = defaultdict(int)  # barriers, persistent over the whole run
    stack = [s]  # search path, node stack
    forbidden = {s}  # nodes on the stack in a set, forbidden for re-visiting
    edges = [None]  # edges[i] enters stack[i]; edges[0] is a dummy
    iters = [iter(succ[s])]  # one successor iterator per frame
    shortest_distances = [_INF]  # per frame: shortest distance to a target

    if s in targets:  # the source is itself a target
        shortest_distances[-1] = 0
        yield []

    def cascade(v, sd):
        """Fruitful write ``b[v] = sd``, then restore (EC) by backward BFS."""
        barrier[v] = sd
        queue = deque([(v, sd)])
        while queue:
            w, d = queue.popleft()
            for u in pred[w]:
                if u not in forbidden and barrier[u] > d + 1:
                    barrier[u] = d + 1  # (EC) was violated at u -> w
                    queue.append((u, d + 1))

    while iters:
        h = len(stack) - 1  # depth of the top node v
        for e in iters[-1]:
            w = e[1]
            if barrier[w] + h < k:  # admissible
                if w == terminal:  # terminal target: report, do not enter
                    yield edges[1:] + [e]
                    if shortest_distances[-1] > 1:
                        shortest_distances[-1] = 1
                elif w not in forbidden:  # descend: call Search(w)
                    stack.append(w)
                    edges.append(e)
                    forbidden.add(w)
                    iters.append(iter(succ[w]))
                    if w in targets:  # a target: report the path on arrival
                        shortest_distances.append(0)
                        yield edges[1:]
                    else:
                        shortest_distances.append(_INF)
                    break
        else:  # return from Search(v)
            v = stack[-1]
            iters.pop()
            sd = shortest_distances.pop()
            if sd <= k:
                cascade(v, sd)  # fruitful; v still forbidden
            else:
                barrier[v] = k - h + 1  # unfruitful raise
            stack.pop()
            edges.pop()
            forbidden.discard(v)
            if shortest_distances and sd + 1 < shortest_distances[-1]:
                shortest_distances[-1] = sd + 1  # propagate distance to caller
