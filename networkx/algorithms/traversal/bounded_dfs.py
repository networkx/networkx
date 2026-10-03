"""Bounded-Scope Depth-First Search (BS-DFS) for length-bounded simple path and cycle enumeration."""


# Implementation overview
# -----------------------
# An iterative depth-limited depth-first search starting at ``s``.
# To prevent excessive fruitless searches, the search is pruned by node barriers.
# To prevent excessive fruitless searches, the search is pruned by node barriers.
# The search is structured using a stack (of nodes forming the path currently
# being considered), the shortest distances found so far to the target from each
# of these nodes, and a *barrier* dict of *certified lower bound* values on the
# number of edges from ``v`` to a target (without using previous nodes on the
# stack). The search tree is pruned whenever the barrier plus the length of stack
# is more than `k`, the bound/scope of the search.
#
# Barriers
# --------
# The search maintains one integer per node, ``barrier[v]``, a *certified lower
# bound* on the number of edges from ``v`` to ``t*`` in the graph minus the nodes
# on the current search path ``[*stack, v]``.  All barriers start at 0, which is
# trivially valid.  At active node ``v`` at depth ``h`` (so ``h`` edges from ``s``
# to ``v``), a successor ``w`` is *admissible* iff
#
#     barrier[w] + h < k                                                   (A)
#
# Rationale: entering ``w`` costs one edge, and ``barrier[w]`` further edges are
# needed before ``t*`` can possibly be reached, so any output through ``w`` has
# length at least ``h + 1 + barrier[w]``; requiring that to be at most ``k`` is
# exactly (A). Because ``barrier[w]`` is a *lower* bound, (A) never discards an
# output: it prunes only branches that provably cannot finish within the budget.
#
# Barriers are updated when the search at ``v`` finishes at depth ``h``.
# Two search results cause an update:
#
# * **fruitless** -- the search at ``v`` produced no output. Its subsearch had a
#   budget of ``k - h`` edges and exhausted it, so ``t*`` is farther than that:
#
#       barrier[v] = k - h + 1                               (a *raise*)
#
# * **fruitful** -- the search at ``v`` produced an output, and ``sd`` is the exact
#   number of edges from ``v`` to ``t*`` along the shortest output found below
#   ``v``. Setting ``barrier[v] = sd`` may *invalidate* barriers of predecessors,
#   which were justified relative to a larger distance from ``v``. A backward BFS
#   restores the invariant
#
#       barrier[u] <= barrier[w] + 1   for every edge u -> w with u not on the path
#
#   ("edge-consistency"), lowering barriers where needed; see ``cascade`` below.
#   Nodes on the current path are skipped: their barriers are written when their
#   searches finish, not while they are on the path.
#
# Edge-consistency is what makes the pop obligation local, and it is why the
# cascade terminates quickly: a node is re-entered by the BFS only when its
# barrier strictly drops, and each barrier only ever moves within ``[0, k+1]``.
#
# Delay (Waiting Time)
# --------------------
# The delay is the time a consumer waits for the first path, for each next path,
# and for exhaustion of a call ``bsdfs(G, s, t, k)``.
# In [1]_ it is proven that within each such waiting time a node is visited
# and an edge is scanned at most 3(k+1) times. Hence the delay is O(k(n+m)),
# where n is the number of nodes reachable from s within the length bound k
# and m the number of edges incident with them (incoming or outgoing).
#
# Prior work
# ----------
# Two earlier papers for the same enumeration problems are listed here as
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
        Source node, where every reported path starts.
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
        The nodes of the path, beginning at ``s`` and ending at the target
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
    Create G from cycles ``[0, 1, 3, 0]``, ``[0, 2, 3, 0]`` and ``[0, 1, 2, 3, 0]``
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
    since no simple path returns to ``s``; ``t == s`` is the way to query for a cycle.

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
    another, so a path from one may pass through another.

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
    stack = {}  # node -> (successor iterator, shortest distance) for suspended frames
    v = s  # v is the current node, initially s
    current_iterator = iter(G_succ[v])
    current_sd = _INF  # shortest distance known to a target from the active node v

    if s in targets:  # the source is itself a target
        current_sd = 0
        yield [s]

    def cascade(v, sd):
        """Fruitfully set ``barrier[v] = sd``, then restore EC by backward BFS."""
        barrier[v] = sd
        queue = deque([v])
        while queue:
            w = queue.popleft()
            dist_u = barrier[w] + 1  # distance for the predecessors u
            for u in G_pred[w]:
                if u not in stack and barrier[u] > dist_u:
                    barrier[u] = dist_u  # (EC) was violated at u -> w
                    queue.append(u)

    while True:
        h = len(stack)  # number of edges in the current search path [*stack, v]
        for w in current_iterator:
            if barrier[w] + h < k:  # node w admissible?
                if w == terminal:  # terminal target: report, do not enter
                    yield [*stack, v, w]
                    current_sd = min(current_sd, 1)  # update shortest distance found
                elif w != v and w not in stack:
                    stack[v] = (current_iterator, current_sd)  # push v and its state
                    v = w
                    current_iterator = iter(G_succ[w])
                    if w in targets:  # a target: report the path on arrival
                        current_sd = 0
                        yield [*stack, v]
                    else:
                        current_sd = _INF
                    break  # descend search to w
        else:  # all descend searches completed, finish search at v
            if not stack:
                return  # v is the root s: search complete, barriers no longer read
            final_sd = current_sd  # shortest distance found among all w
            if final_sd <= k:
                cascade(v, final_sd)  # fruitful cascade
            else:
                barrier[v] = k - h + 1  # fruitless raise
            v, (current_iterator, current_sd) = stack.popitem()  # pop parent node
            current_sd = min(final_sd + 1, current_sd)  # update shortest distance


@nx._dispatchable
def bsdfs_edges(G, s, t, k):
    """Yield the paths of :func:`bsdfs` as edge lists rather than node lists.

    This is to :func:`bsdfs` what
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths` is to
    :func:`~networkx.algorithms.simple_paths.all_simple_paths`.  The search
    is identical; only the reporting differs.  On a multigraph one node path
    corresponds to several edge paths, one per combination of parallel edge
    keys, and all of them are yielded.

    Parameters
    ----------
    G : NetworkX graph
        Directed or undirected, graph or multigraph.
    s : node
        Source node, where every reported path starts.
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
        The edges of the path, as ``(u, v)``, resp. ``(u, v, key)`` on a
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

    Parallel edges give one path each, distinguished by their key.

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
    paths = bsdfs(G, s, t, k)
    if G.is_multigraph():
        for path in paths:
            choices = [[(u, v, key) for key in G[u][v]] for u, v in zip(path, path[1:])]
            yield from (list(c) for c in itertools.product(*choices))
    else:
        for path in paths:
            yield [(u, v) for u, v in zip(path, path[1:])]
