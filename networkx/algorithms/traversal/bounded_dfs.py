"""Bounded-Scope Depth-First Search (BS-DFS) for legnth bound path/cycle enumeration"""


# :func:`bsdfs` enumerates all length bounded simple paths or cycles
# in a graph extending a given prefix path.

# :func:`bsdfs` is used in NetworkX functions `all_simple_edge_paths` and
# `simple_cycles` when a length bound is specified.

# Cycle mode and path mode
# ------------------------
# The two modes differ in one bit, selected by ``targets``:

# * ``targets is None`` -- *cycle mode*.  The implied target is ``prefix[0]``,
#   so the walk reported returns to the node it started from.
# * ``targets`` a set -- *path mode*.  The walk reported ends at a target.
#   Targets are otherwise ordinary nodes, so a walk may run through one on its
#   way to another.

# In path mode ``prefix`` and ``targets`` need not be disjoint, but a target on
# the prefix cannot be reached again.  The only visible effect is that
# ``prefix[-1] in targets`` yields the empty extension, which is NetworkX's
# trivial path.

# Implementation overview
# -----------------------
# An iterative depth-limited depth-first search starting at ``prefix[-1]``.
# A set of forbidden nodes -- the prefix, plus everything currently on the search
# stack -- keeps the reported walks simple.

# The modes differ only in how the last step is taken.  In cycle mode the root
# stays forbidden and is never entered, so the edge ``v -> prefix[0]`` is reported
# where it is found and consumes one edge of the bound.  In path mode a target
# is entered like any other node and the path ending there is reported on
# arrival, consuming nothing further.  Both are the same rule seen through a
# virtual target ``t*``, joined to every target by an edge of length 1 resp. 0.

# To prevent excessive fruitless searches, the search is pruned by node barriers.

# Barriers
# --------
# The search maintains one integer per node, ``b[v]``, a *certified lower bound*
# on the number of edges from ``v`` to ``t*`` in the graph minus the nodes
# currently on the search stack ``stack``.  All barriers start at 0, which is
# trivially valid.  With ``v`` on top of ``stack`` at depth ``h`` (so ``h`` edges
# from the root to ``v``), a successor ``w`` is *admissible* iff

#     b[w] + h < k                                                        (A)

# Rationale: entering ``w`` costs one edge, and ``b[w]`` further edges are needed
# before ``t*`` can possibly be reached, so any output through ``w`` has length
# at least ``h + 1 + b[w]``; requiring that to be at most ``k`` is exactly (A).
# Because ``b[w]`` is a *lower* bound, (A) never discards an output: it prunes
# only branches that provably cannot finish within the budget.

# Barriers are written in exactly two places, both on return from ``Search(v)``
# with ``v`` at depth ``h``:

# * **unfruitful return** -- ``v`` produced no output.  The subsearch had a
#   budget of ``k - h`` edges and exhausted it, so ``t*`` is farther than that:

#       b[v] = k - h + 1                                    (a *raise*)

# * **fruitful return** -- ``v`` produced an output, and ``sd`` is the exact
#   number of edges from ``v`` to ``t*`` along the shortest output found below
#   ``v``.  Setting ``b[v] = sd`` may *invalidate* the barriers of predecessors,
#   which were justified relative to a larger distance from ``v``.  A backward
#   BFS restores the invariant

#       b[u] <= b[w] + 1     for every edge u -> w with u not on stack       (EC)

#   ("edge-consistency"), lowering barriers where needed; see ``cascade`` below.
#   Nodes on ``stack`` are skipped: their barriers are written when they are popped,
#   not while they are forbidden.

# Edge-consistency is what makes the pop obligation local, and it is why the
# cascade terminates quickly: a node is re-entered by the BFS only when its
# barrier strictly drops, and each barrier only ever moves within ``[0, k+1]``.

# Delay
# -----
# Every cascade is triggered by a fruitful return, i.e. it is charged to an
# output that has already been emitted.  Together with the raise bound this
# gives worst-case delay ``3(k+1)(n+m)`` and amortized delay ``2(k+1)(n+m)``,
# with ``n`` nodes and ``m`` edges -- in particular ``O(k(n+m))`` with a small
# constant.  See [1]_.

# Prior work
# ----------
# Two earlier algorithms for the same enumeration problems are listed here as
# prior art, not as alternatives: [1]_ and [2]_ demonstrate inputs on which
# [3]_ and [4]_ omit valid outputs.

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


_NO_ROOT = object()  # sentinel: never equal to any node


class _OutEdgeCache(dict):
    """Caches, per node, the list of its outgoing edges as tuples.

    Same purpose as ``_NeighborhoodCache`` in ``cycles.py`` -- avoid the
    per-access cost of subgraph views -- but stores edge tuples ``(v, w)``,
    resp. ``(v, w, key)`` for multigraphs, since the path caller needs the
    multigraph key and cannot recover it from the node sequence.
    """

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
def bsdfs(G, prefix, targets, k):
    """Yield all length bounded simple paths or cycles extending prefix to targets.

    Parameters
    ----------
    G : NetworkX graph
        Directed or undirected, graph or multigraph.
    prefix : list
        Non-empty prefix, a simple path in ``G`` given as a node list.
        Not mutated.
    targets : set or None
        Target nodes, or ``None`` to search for cycles starting with ``prefix``.
        Not mutated.
    k : int
        Length bound in edges, counted from ``prefix[0]``, i.e. the prefix
        already consumes ``len(prefix) - 1`` of the budget.

    Yields
    ------
    list of edges
        The edges extending ``prefix[-1]`` to some node in ``targets``.
        If ``targets`` is ``None``, cycles to ``prefix[0]`` are yielded.

    Raises
    ------
    ValueError
        If ``k`` is negative, ``prefix`` is empty, or ``targets`` is an empty set.
    NodeNotFound
        If a node of ``prefix`` is not in ``G``.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])

    Cycle mode.  The cycle 0, 1, 2, 3 has 4 edges and exceeds the bound, so
    only two are reported.  The caller prepends the prefix to obtain nodes.

    >>> list(bsdfs(G, [0], None, 3))
    [[(0, 1), (1, 3), (3, 0)], [(0, 2), (2, 3), (3, 0)]]
    >>> [[e[0] for e in E] for E in bsdfs(G, [0], None, 3)]
    [[0, 1, 3], [0, 2, 3]]

    A longer prefix restricts the search, and only the extension is reported.

    >>> list(bsdfs(G, [0, 1], None, 3))
    [[(1, 3), (3, 0)]]
    >>> [[0] + [e[0] for e in E] for E in bsdfs(G, [0, 1], None, 3)]
    [[0, 1, 3]]

    Path mode, to one target and to a set of targets.  Targets are entered
    like any other node, so 0, 1, 2, 3 is reported although it runs through
    the target 2.

    >>> list(bsdfs(G, [0], {3}, 3))
    [[(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2), (2, 3)]]
    >>> list(bsdfs(G, [0], {2, 3}, 3))
    [[(0, 1), (1, 2)], [(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2)], [(0, 2), (2, 3)]]

    A target on the prefix is forbidden and cannot be entered again, so
    ``prefix[-1]`` in ``targets`` adds the empty extension and nothing else.

    >>> list(bsdfs(G, [0], {0, 3}, 3))
    [[], [(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2), (2, 3)]]

    See Also
    --------
    all_simple_edge_paths, all_simple_paths, simple_cycles

    Notes
    -----
    Between consecutive outputs the algorithm performs at most
    ``3(k+1)(n+m)`` elementary steps on a graph with ``n`` nodes and ``m``
    edges, and at most ``2(k+1)(n+m)`` amortized over all outputs [1]_.
    One elementary step is a single adjacency-list entry scanned, plus
    constant bookkeeping per call and per barrier update, so the delay is
    ``O(k(n+m))``.  The module docstring describes the node barriers this
    rests on, and relates the algorithm to earlier, incomplete ones.

    References
    ----------
    .. [1] Frank Bauernoeppel, Joerg-Ruediger Sack,
        "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
        with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers", 2026,
        https://arxiv.org/abs/2607.14745
    """

    if k < 0:
        raise ValueError(f"length bound {k=} must be non-negative")
    if not prefix:
        raise ValueError(f"{prefix=} must be a non-empty list of nodes")
    for v in prefix:
        if v not in G:
            raise nx.NodeNotFound(f"prefix node {v} not in graph")
    if targets is not None and not targets:
        raise ValueError(f"{targets=} must be None or a non-empty set of nodes")

    succ = _OutEdgeCache(G)
    pred = _InNodeCache(G.pred if G.is_directed() else G.adj)

    if targets is None:  # cycle mode: only the root is a target
        cycle_root, targets = prefix[0], frozenset()
    else:  # path mode: no cycle is closed
        cycle_root = _NO_ROOT

    barrier = defaultdict(int)  # barriers, persistent over the whole run
    stack = list(prefix)  # node stack; do not mutate the caller's list
    plen = len(stack)  # where the reported edge list starts
    forbidden = set(stack)  # node set on stack, forbidden for re-visiting
    edges = [None] * plen  # edges[i] enters stack[i]; prefix part unused
    iters = [iter(succ[stack[-1]])]  # only the last prefix node gets a frame
    shortest_distances = [k + 1]  # per frame: shortest distance to t* found below

    if stack[-1] in targets and plen - 1 <= k:  # the prefix already ends at a target
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
                if w == cycle_root:  # the root is forbidden: close, do not push
                    yield edges[plen:] + [e]
                    if shortest_distances[-1] > 1:
                        shortest_distances[-1] = 1
                elif w not in forbidden:  # descend: call Search(w)
                    stack.append(w)
                    edges.append(e)
                    forbidden.add(w)
                    iters.append(iter(succ[w]))
                    if w in targets:  # a target: report the path on arrival
                        shortest_distances.append(0)
                        yield edges[plen:]
                    else:
                        shortest_distances.append(k + 1)
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
