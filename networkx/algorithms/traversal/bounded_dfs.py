"""Algorithms for simple path and cycle enumeration with a length bound."""


# Implementation overview
# -----------------------
# An iterative depth-first type of search starting at `source` (``s``) and
# terminating in a node ``t``, with at most `length_bound` (``k``) edges per
# output.  If `target` is ``None``, ``t`` is ``s`` and the outputs are cycles.
# Otherwise ``t`` is `target`, a single node or any node of a set, and the
# outputs are paths.  We use two variables to handle these cases:
#
#     parameter: `target`    var: ``terminal``  var: ``targets``
#     ---------------------  -----------------  ----------------------------
#     ``None`` (cycles)      `source`           empty set
#     a node or node set*    dummy              ``{target}`` or ``set(target)``
#
#  * A single target ``t != s``, a node ``t`` or a one-node set ``{t}``, is
#    handled as ``terminal = t`` with empty ``targets``, for performance.
#
# Paths arriving at ``terminal`` are yielded and no further extension is explored,
# i.e. no paths pass through ``terminal``.  If ``terminal == source`` then the
# paths are cycles. The dummy value for ``terminal`` is ``object()`` which equals
# no node. The nodes of ``targets`` are entered like other nodes, a path is reported
# on arrival, and the search continues through them.
#
# The search is structured using a dict as stack.  Its keys are the suspended nodes
# of the current search path ``P = [*stack, v]``, in path order.  Its values hold,
# for each of these nodes, the successor iterator to resume from and the shortest
# distance to ``t`` found so far.  In addition, one integer *barrier* per node
# is maintained in a dict for preventing repeated fruitless searches.
#
# Barriers
# --------
# ``barrier[x]`` is a *certified lower bound* on the number of edges from ``x``
# to ``t`` in the graph minus the nodes on ``P``.  All barriers start at 0,
# which is trivially valid.  At active node ``v`` at depth ``h`` (so ``h`` edges
# from ``s`` to ``v``), a successor ``w`` is *admissible* iff
#
#     barrier[w] + h < k                                                   (A)
#
# Rationale: entering ``w`` costs one edge, and ``barrier[w]`` further edges are
# needed before ``t`` can possibly be reached, so any output through ``w`` has
# length at least ``h + 1 + barrier[w]``; requiring that to be at most ``k`` is
# exactly (A). Because ``barrier[w]`` is a *lower* bound, (A) never discards an
# output: it prunes only branches that provably cannot finish within the budget.
#
# Barriers are updated when the search at ``v`` finishes at depth ``h``.
# Two search results are possible which we call **fruitless** and **fruitful**:
#
# * **fruitless** -- the search at ``v`` produced no output. Its subsearch had a
#   budget of ``k - h`` edges and exhausted it, so ``t`` is farther than that,
#   or every route within that budget is currently blocked by nodes already on
#   the search path. We update the barrier value:
#
#       barrier[v] = k - h + 1
#
# * **fruitful** -- the search at ``v`` produced an output, and ``sd`` is the exact
#   number of edges from ``v`` to ``t`` along the shortest output found below ``v``.
#   When ``v`` leaves the path, barriers of predecessors raised while ``v`` blocked
#   their routes may now be too high. A backward BFS lowers barriers where needed
#   and restores the "edge-consistency" (EC) invariant; see ``cascade`` below. Thus:
#
#       barrier[v] = sd
#       barrier[u] <= barrier[w] + 1  for every edge u -> w with u and w not on the path
#
#   Nodes on the current path are skipped: their barriers are written when their
#   searches finish, not while they are on the path.
#
# EC together with barrier[t] == 0 implies the lower-bound property: along
# any path x = x0, ..., xj = t in G - P, barrier[x0] <= barrier[x1] + 1
# <= ... <= j.  So when v leaves the path, only EC on edges u -> v must be
# re-established.
#
# Path length ``h`` and barriers thus jointly bound the *scope* of the search,
# which results in a delay of O(k(n+m)) per output; see the Notes of ``bsdfs``
# docstring for the exact bounds and [1] for the proofs.
#
# References
# ----------
# .. [1] Frank Bauernöppel, Jörg-Rüdiger Sack,
#     "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
#     with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers", 2026,
#     https://arxiv.org/abs/2607.14745

import itertools
from collections import defaultdict, deque

import networkx as nx

__all__ = ["bsdfs", "bsdfs_edges"]


@nx._dispatchable
def bsdfs(G, source, target=None, *, length_bound):
    """Yield all length-bounded simple paths or cycles starting at `source`.

    Bounded-Scope Depth-First Search (BS-DFS) yields every simple path from
    `source` to `target` with at most `length_bound` edges, or every such
    simple cycle through `source` if `target` is None.
    Unlike :func:`~networkx.algorithms.traversal.depth_first_search.dfs_edges`,
    which visits each node once and yields the edges of a single search
    tree, it yields every such path.

    Together with the length bound, per-node barriers limit the *scope*
    of the search, hence the name. As a result, the *delay*, the time until
    the next output or until the search ends, is ``O(k(n+m))`` (see Notes),
    whereas a plain depth-limited search can spend time exponential in
    `length_bound` on dead ends.

    Parameters
    ----------
    G : NetworkX graph
        Directed or undirected; multigraphs are allowed.
    source : node
        Source node, where every reported path or cycle starts.
    target : node or set of nodes, optional
        If None (the default), the simple cycles through `source` are enumerated.
        A single node enumerates the simple paths from `source` to `target`.
        A set enumerates the simple paths from `source` to any node of the set,
        and such a path may pass through one node of the set on its way to
        another.  A single node and the corresponding one-element set give
        the same paths.
    length_bound : int
        Length bound in edges.

    Yields
    ------
    list of nodes
        The nodes of the path, beginning at `source` and ending at the target
        reached, or the nodes of the cycle, beginning and ending at `source`.
        All nodes are distinct, except for the repeated `source` of a cycle.
        The one-node list ``[source]`` is yielded for the trivial path, i.e.
        when `source` is among the targets.

        On undirected graphs (``Graph`` or ``MultiGraph``), the cycle search
        may return to `source` along the edge it left by,
        so ``[source, u, source]`` is reported for every neighbor ``u``, and every
        longer cycle is reported twice, once per orientation. Use
        :func:`~networkx.algorithms.cycles.simple_cycles` for the cycles of an
        undirected graph. Paths are not affected. On multigraphs,
        each node path is reported once; :func:`bsdfs_edges` yields one edge
        path per combination of parallel edges.

    Raises
    ------
    ValueError
        If `length_bound` is negative, or `target` is an empty set.
    NodeNotFound
        If `source` is not in `G`, or `target` is neither a node of `G` nor a
        set of nodes.

    Examples
    --------
    Create G from cycles ``[0, 1, 3, 0]``, ``[0, 2, 3, 0]`` and ``[0, 1, 2, 3, 0]``.

    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])

    Without `target` these are the cycles through `source`, ending at `source`
    again.  The 4-edge cycle 0, 1, 2, 3 exceeds the bound.

    >>> list(bsdfs(G, source=0, length_bound=3))
    [[0, 1, 3, 0], [0, 2, 3, 0]]

    Cycles through the edge (0, 1) are the paths from 1 back to 0, with one
    edge of the bound already spent by that edge.

    >>> list(bsdfs(G, 1, 0, length_bound=2))
    [[1, 3, 0]]

    A set of targets may be passed through, so 0, 1, 2, 3 is reported
    although it runs through the target 2.  A single node and the matching
    one-element set agree.

    >>> list(bsdfs(G, 0, {2, 3}, length_bound=3))
    [[0, 1, 2], [0, 1, 2, 3], [0, 1, 3], [0, 2], [0, 2, 3]]
    >>> list(bsdfs(G, 0, {3}, length_bound=3)) == list(bsdfs(G, 0, 3, length_bound=3))
    True

    `source` as a target, alone or in a set, yields the trivial path ``[source]``
    but no cycle, since no simple path returns to `source`.

    >>> list(bsdfs(G, 0, 0, length_bound=3))
    [[0]]
    >>> list(bsdfs(G, 0, {0, 3}, length_bound=3))
    [[0], [0, 1, 2, 3], [0, 1, 3], [0, 2, 3]]

    See Also
    --------
    :func:`bsdfs_edges`
    :func:`~networkx.algorithms.simple_paths.all_simple_paths`
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths`
    :func:`~networkx.algorithms.cycles.simple_cycles`

    Notes
    -----
    The *delay* is the time a consumer waits for the first path, for each next
    path, and for exhaustion of the generator. The delay is at most
    ``3(k+1)(n+m)`` elementary steps, and the first ``p`` outputs are
    generated in at most ``2p(k+1)(n+m)`` elementary steps [1]_.
    Here ``k`` is `length_bound`, ``n`` is the number of nodes reachable from `source`
    within ``k`` edges, and ``m`` the number of edges incident with them (incoming or
    outgoing). An elementary step is a node visit, the output of one node of a path,
    or the scan of a single adjacency-list entry.

    A search from several sources is obtained by adding a virtual source node
    joined to each of them, running with the length bound increased by 1, and dropping
    the leading virtual edge from each result.  The sources do not block one
    another, so a path from one may pass through another.

    References
    ----------
    .. [1] Frank Bauernöppel, Jörg-Rüdiger Sack,
        "Enumerating Length-Bounded Simple Paths and Cycles in Directed Graphs
        with $O(k(n+m))$ Delay Using Edge-Consistent Node Barriers", 2026,
        https://arxiv.org/abs/2607.14745
    """

    if length_bound < 0:
        raise ValueError(f"length bound {length_bound} must be non-negative")
    if source not in G:
        raise nx.NodeNotFound(f"source node {source} not in graph")

    if target is None:  # cycles through source, as in the paper
        terminal, targets = source, frozenset()
    else:  # paths to a node or a set of nodes
        if target in G:
            targets = {target}
        else:
            try:
                targets = set(target)
            except TypeError as err:
                raise nx.NodeNotFound(
                    f"target {target!r} is neither a node of G nor an iterable of nodes"
                ) from err
            if not targets:
                raise ValueError(
                    f"{target=} must be a node or a non-empty set of nodes"
                )
        if len(targets) == 1 and source not in targets:
            (terminal,) = targets  # a single target, as in the paper
            targets = frozenset()
        else:  # NetworkX extension: targets are entered
            terminal = object()  # dummy node; never equal to any node in G

    G_succ = G._succ if G.is_directed() else G._adj
    G_pred = G._pred if G.is_directed() else G._adj

    barrier = defaultdict(int)  # barriers, persistent over the whole run
    stack = {}  # node -> (successor iterator, shortest distance) for suspended frames
    no_sd = length_bound + 1  # shortest distance - init value; real ones are smaller

    v = source  # v is the current node, initially source
    current_iterator = iter(G_succ[v])
    current_sd = no_sd  # shortest distance known to a target from the active node v

    if source in targets:  # the source is itself a target
        current_sd = 0
        yield [source]

    def cascade(v, sd):
        """Fruitfully set ``barrier[v] = sd``, then restore EC by backward BFS."""
        barrier[v] = sd
        queue = deque([v])
        while queue:
            w = queue.popleft()
            dist_u = barrier[w] + 1  # distance for the predecessors u
            for u in G_pred[w]:
                if barrier[u] > dist_u and u not in stack:
                    barrier[u] = dist_u  # (EC) was violated at u -> w
                    queue.append(u)

    while True:
        h = len(stack)  # number of edges in the current search path [*stack, v]
        for w in current_iterator:
            if barrier[w] + h < length_bound:  # node w admissible?
                if w == terminal:  # terminal target: report, do not enter
                    yield [*stack, v, w]
                    current_sd = 1  # shortest distance found
                elif w != v and w not in stack:
                    stack[v] = (current_iterator, current_sd)  # push v and its state
                    v = w
                    current_iterator = iter(G_succ[w])
                    if w in targets:  # a target: report the path on arrival
                        current_sd = 0
                        yield [*stack, v]
                    else:
                        current_sd = no_sd
                    break  # descend search to w
        else:  # all descend searches completed, finish search at v
            if not stack:
                return  # v is the root node: search complete, barriers no longer read
            final_sd = current_sd  # shortest distance found among all w
            if final_sd < no_sd:  # some path to target found
                cascade(v, final_sd)  # fruitful cascade, update barriers
            else:
                barrier[v] = length_bound - h + 1  # fruitless raise, own barrier
            v, (current_iterator, current_sd) = stack.popitem()  # pop parent node
            if final_sd < current_sd:  # update shortest distance
                current_sd = final_sd + 1


@nx._dispatchable
def bsdfs_edges(G, source, target=None, *, length_bound):
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
        Directed or undirected; multigraphs are allowed.
    source : node
        Source node, where every reported path or cycle starts.
    target : node or set of nodes, optional
        If None (the default), the simple cycles through `source` are enumerated.
        A single node enumerates the simple paths from `source` to `target`.
        A set enumerates the simple paths from `source` to any node of the set,
        and such a path may pass through one node of the set on its way to
        another.  A single node and the corresponding one-element set give
        the same paths.
    length_bound : int
        Length bound in edges.

    Yields
    ------
    list of edges
        The edges of the path or cycle, as ``(u, v)``, or ``(u, v, key)`` on a
        multigraph.  The empty list is yielded for the trivial path, i.e.
        when `source` is among the targets.

        On undirected graphs (``Graph`` or ``MultiGraph``), the cycle search
        may return to `source` along the edge it left by,
        so ``[(source, u), (u, source)]`` is reported for every neighbor ``u``, and every
        longer cycle is reported twice, once per orientation. Use
        :func:`~networkx.algorithms.cycles.simple_cycles` for the cycles of an
        undirected graph. Paths are not affected.

    Raises
    ------
    ValueError
        If `length_bound` is negative, or `target` is an empty set.
    NodeNotFound
        If `source` is not in `G`, or `target` is neither a node of `G` nor a
        set of nodes.

    Examples
    --------
    Create G from cycles ``[0, 1, 3, 0]``, ``[0, 2, 3, 0]`` and ``[0, 1, 2, 3, 0]``.

    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (1, 3), (2, 3), (3, 0)])
    >>> list(bsdfs_edges(G, source=0, target=3, length_bound=3))
    [[(0, 1), (1, 2), (2, 3)], [(0, 1), (1, 3)], [(0, 2), (2, 3)]]

    Parallel edges give one path each, distinguished by their key.

    >>> M = nx.MultiDiGraph([(0, 1), (0, 1), (1, 2)])
    >>> list(bsdfs(M, 0, 2, length_bound=3))
    [[0, 1, 2]]
    >>> list(bsdfs_edges(M, 0, 2, length_bound=3))
    [[(0, 1, 0), (1, 2, 0)], [(0, 1, 1), (1, 2, 0)]]

    See Also
    --------
    :func:`bsdfs`
    :func:`~networkx.algorithms.simple_paths.all_simple_edge_paths`

    Notes
    -----
    The ``O(k(n+m))`` delay of :func:`bsdfs` carries over, see its Notes.
    """
    paths = bsdfs(G, source, target, length_bound=length_bound)
    if G.is_multigraph():
        product = itertools.product
        for path in paths:
            nodepairs = nx.utils.pairwise(path)
            choices = [[(u, v, key) for key in G[u][v]] for u, v in nodepairs]
            yield from (list(c) for c in product(*choices))
    else:
        for path in paths:
            yield list(nx.utils.pairwise(path))
