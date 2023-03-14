"""
========================
Cycle finding algorithms
========================
"""

from collections import defaultdict

import networkx as nx
from networkx.utils import not_implemented_for, pairwise

__all__ = [
    "cycle_basis",
    "simple_cycles",
    "recursive_simple_cycles",
    "find_cycle",
    "minimum_cycle_basis",
]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def cycle_basis(G, root=None):
    """Returns a list of cycles which form a basis for cycles of G.

    A basis for cycles of a network is a minimal collection of
    cycles such that any cycle in the network can be written
    as a sum of cycles in the basis.  Here summation of cycles
    is defined as "exclusive or" of the edges. Cycle bases are
    useful, e.g. when deriving equations for electric circuits
    using Kirchhoff's Laws.

    Parameters
    ----------
    G : NetworkX Graph
    root : node, optional
       Specify starting node for basis.

    Returns
    -------
    A list of cycle lists.  Each cycle list is a list of nodes
    which forms a cycle (loop) in G.

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_cycle(G, [0, 1, 2, 3])
    >>> nx.add_cycle(G, [0, 3, 4, 5])
    >>> print(nx.cycle_basis(G, 0))
    [[3, 4, 5, 0], [1, 2, 3, 0]]

    Notes
    -----
    This is adapted from algorithm CACM 491 [1]_.

    References
    ----------
    .. [1] Paton, K. An algorithm for finding a fundamental set of
       cycles of a graph. Comm. ACM 12, 9 (Sept 1969), 514-518.

    See Also
    --------
    simple_cycles
    """
    gnodes = set(G.nodes())
    cycles = []
    while gnodes:  # loop over connected components
        if root is None:
            root = gnodes.pop()
        stack = [root]
        pred = {root: root}
        used = {root: set()}
        while stack:  # walk the spanning tree finding cycles
            z = stack.pop()  # use last-in so cycles easier to find
            zused = used[z]
            for nbr in G[z]:
                if nbr not in used:  # new node
                    pred[nbr] = z
                    stack.append(nbr)
                    used[nbr] = {z}
                elif nbr == z:  # self loops
                    cycles.append([z])
                elif nbr not in zused:  # found a cycle
                    pn = used[nbr]
                    cycle = [nbr, z]
                    p = pred[z]
                    while p not in pn:
                        cycle.append(p)
                        p = pred[p]
                    cycle.append(p)
                    cycles.append(cycle)
                    used[nbr].add(z)
        gnodes -= set(pred)
        root = None
    return cycles


def simple_cycles(G, k=None):
    """Find simple cycles (elementary circuits) of a graph.

    A `simple cycle`, or `elementary circuit`, is a closed path where
    no node appears twice.  In a directed graph, two simple cycles are distinct
    if they are not cyclic permutations of each other.  In an undirected graph,
    two simple cycles are distinct if they are not cyclic permutations of each
    other nor of the other's reversal.

    Optionally, the cycles are bounded in length by the parameter k.  In the
    unbounded case, we use a nonrecursive, iterator/generator version of
    Johnson's algorithm [1]_.  In the bounded case, we use a version of the
    algorithm of Gupta and Suzumura [2]_. There may be better algorithms for
    some cases [3]_ [4]_ [5]_.

    The algorithms of Johnson, and Gupta and Suzumura, are enhanced by some
    well-known preprocessing techniques.  When G is directed, we restrict our
    attention to strongly connected components of G, generate all simple cycles
    containing a certain node, remove that node, and further decompose the
    remainder into strongly connected components.  When G is undirected, we
    restrict our attention to biconnected components, generate all simple cycles
    containing a particular edge, remove that edge, and further decompose the
    remainder into biconnected components.


    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    k : int or None
       If k is an int, generate all simple cycles of G with length at most k.
       Otherwise, generate all simple cycles of G.

    Yields
    ------
    list of nodes
       Each cycle is represented by a list of nodes along the cycle.

    Examples
    --------
    >>> edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    >>> G = nx.DiGraph(edges)
    >>> sorted(nx.simple_cycles(G))
    [[0], [0, 1, 2], [0, 2], [1, 2], [2]]

    To filter the cycles so that they don't include certain nodes or edges,
    copy your graph and eliminate those nodes or edges before calling.
    For example, to exclude self-loops from the above example:

    >>> H = G.copy()
    >>> H.remove_edges_from(nx.selfloop_edges(G))
    >>> sorted(nx.simple_cycles(H))
    [[0, 1, 2], [0, 2], [1, 2]]

    Notes
    -----
    When k is None, the time complexity is $O((n+e)(c+1))$ for $n$ nodes, $e$
    edges and $c$ simple circuits.  Otherwise, when $k > 1$, the time complexity
    is $O((c+n)(k-1)d^k)$ where $d$ is the average degree of the nodes of G.

    References
    ----------
    .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       https://doi.org/10.1137/0204007
    .. [2] Finding All Bounded-Length Simple Cycles in a Directed Graph
       A. Gupta and T. Suzumura https://arxiv.org/abs/2105.10094
    .. [3] Enumerating the cycles of a digraph: a new preprocessing strategy.
       G. Loizou and P. Thanish, Information Sciences, v. 27, 163-182, 1982.
    .. [4] A search strategy for the elementary cycles of a directed graph.
       J.L. Szwarcfiter and P.E. Lauer, BIT NUMERICAL MATHEMATICS,
       v. 16, no. 2, 192-204, 1976.
    .. [5] Optimal Listing of Cycles and st-Paths in Undirected Graphs
        R. Ferreira and R. Grossi and A. Marino and N. Pisanti and R. Rizzi and
        G. Sacomoto https://arxiv.org/abs/1205.2766

    See Also
    --------
    cycle_basis
    """
    if k is not None:
        if k == 0:
            return
        elif k < 0:
            raise ValueError("length bound must be non-negative")

    directed = G.is_directed()
    yield from ([v] for v in G if v in G[v])

    if directed:
        G = nx.DiGraph((u, v) for u in G for v in G[u] if v != u)
    else:
        G = nx.Graph((u, v) for u in G for v in G[u] if v != u)

    if directed:
        yield from _directed_cycle_search(G, k)
    else:
        yield from _undirected_cycle_search(G, k)


def _directed_cycle_search(G, k):
    """A dispatch function for `simple_cycles` for directed graphs.

    We generate all cycles of G through binary partition.

        1. Pick a node v in G which belongs to at least one cycle
            a. Generate all cycles of G which contain the node v.
            b. Recursively generate all cycles of G \\ v.

    This is accomplished through the following:

        1. Compute the strongly connected components SCC of G.
        2. Select and remove a biconnected component C from BCC.  Select a
           non-tree edge (u, v) of a depth-first search of G[C].
        3. For each simple cycle P containing v in G[C], yield P.
        4. Add the biconnected components of G[C \\ v] to BCC.

    If the parameter k is not None, then step 3 will be limited to simple cycles
    of length at most k.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph

    k : int or None
       If k is an int, generate all simple cycles of G with length at most k.
       Otherwise, generate all simple cycles of G.

    Yields
    ------
    list of nodes
       Each cycle is represented by a list of nodes along the cycle.
    """

    scc = nx.strongly_connected_components
    components = [c for c in scc(G) if len(c) >= 2]
    while components:
        c = components.pop()
        Gc = G.subgraph(c)
        v = next(iter(c))
        if k is None:
            yield from _johnson_cycle_search(Gc, [v])
        else:
            yield from _bounded_cycle_search(Gc, [v], k)
        # delete v after searching G, to make sure we can find v
        G.remove_node(v)
        components.extend(c for c in scc(Gc) if len(c) >= 2)


def _undirected_cycle_search(G, k):
    """A dispatch function for `simple_cycles` for undirected graphs.

    We generate all cycles of G through binary partition.

        1. Pick an edge (u, v) in G which belongs to at least one cycle
            a. Generate all cycles of G which contain the edge (u, v)
            b. Recursively generate all cycles of G \\ (u, v)

    This is accomplished through the following:

        1. Compute the biconnected components BCC of G.
        2. Select and remove a biconnected component C from BCC.  Select a
           non-tree edge (u, v) of a depth-first search of G[C].
        3. For each (v -> u) path P remaining in G[C] \\ (u, v), yield P.
        4. Add the biconnected components of G[C] \\ (u, v) to BCC.

    If the parameter k is not None, then step 3 will be limited to simple paths
    of length at most k.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph

    k : int or None
       If k is an int, generate all simple cycles of G with length at most k.
       Otherwise, generate all simple cycles of G.

    Yields
    ------
    list of nodes
       Each cycle is represented by a list of nodes along the cycle.
    """

    bcc = nx.biconnected_components
    components = [c for c in bcc(G) if len(c) >= 3]
    while components:
        c = components.pop()
        Gc = G.subgraph(c)
        uv = list(next(iter(Gc.edges)))
        G.remove_edge(*uv)
        # delete (u, v) before searching G, to avoid fake 3-cycles [u, v, u]
        if k is None:
            yield from _johnson_cycle_search(Gc, uv)
        else:
            yield from _bounded_cycle_search(Gc, uv, k)
        components.extend(c for c in bcc(Gc) if len(c) >= 3)


class _NeighborhoodCache(dict):
    """Very lightweight graph wrapper which caches neighborhoods as sets.

    This dict subclass uses the __missing__ functionality to query graphs for
    their neighborhoods, and store the result as a set.  This is used to avoid
    the performance penalty incurred by subgraph views.
    """

    def __init__(self, G):
        self.G = G

    def __missing__(self, v):
        Gv = self[v] = set(self.G[v])
        return Gv


def _johnson_cycle_search(G, path):
    """The main loop of the cycle-enumeration algorithm of Johnson.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph

    path : list
       A cycle prefix.  All cycles generated will begin with this prefix.

    Yields
    ------
    list of nodes
       Each cycle is represented by a list of nodes along the cycle.

    References
    ----------
        .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       https://doi.org/10.1137/0204007

    """

    G = _NeighborhoodCache(G)
    blocked = set(path)
    B = defaultdict(set)  # graph portions that yield no elementary circuit
    start = path[0]
    stack = [iter(G[path[-1]])]
    closed = [False]
    while stack:
        nbrs = stack[-1]
        for w in nbrs:
            if w == start:
                yield path[:]
                closed[-1] = True
            elif w not in blocked:
                path.append(w)
                closed.append(False)
                stack.append(iter(G[w]))
                blocked.add(w)
                break
        else:  # no more nbrs
            stack.pop()
            v = path.pop()
            if closed.pop():
                if closed:
                    closed[-1] = True
                unblock_stack = {v}
                while unblock_stack:
                    u = unblock_stack.pop()
                    if u in blocked:
                        blocked.remove(u)
                        unblock_stack.update(B[u])
                        B[u].clear()
            else:
                for w in G[v]:
                    B[w].add(v)


def _bounded_cycle_search(G, path, k):
    """The main loop of the cycle-enumeration algorithm of Gupta and Suzumura.

    Parameters
    ----------
    G : NetworkX Graph
       An undirected graph

    path : list
       A cycle prefix.  All cycles generated will begin with this prefix.

    k: int
        A length bound.  All cycles generated will have length at most k.

    Yields
    ------
    list of nodes
       Each cycle is represented by a list of nodes along the cycle.

    References
    ----------
        .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       https://doi.org/10.1137/0204007

    """
    G = _NeighborhoodCache(G)
    lock = {v: 0 for v in path}
    B = defaultdict(set)
    start = path[0]
    stack = [iter(G[path[-1]])]
    blen = [k]
    while stack:
        nbrs = stack[-1]
        for w in nbrs:
            if w == start:
                yield path[:]
                blen[-1] = 1
            elif len(path) < lock.get(w, k):
                path.append(w)
                blen.append(k)
                lock[w] = len(path)
                stack.append(iter(G[w]))
                break
        else:
            stack.pop()
            v = path.pop()
            bl = blen.pop()
            if blen:
                blen[-1] = min(blen[-1], bl)
            if bl < k:
                relax_stack = [(bl, v)]
                while relax_stack:
                    bl, u = relax_stack.pop()
                    if lock.get(u, k) < k - bl + 1:
                        lock[u] = k - bl + 1
                        relax_stack.extend((bl + 1, w) for w in B[u].difference(path))
            else:
                for w in G[v]:
                    B[w].add(v)


@not_implemented_for("undirected")
def recursive_simple_cycles(G):
    """Find simple cycles (elementary circuits) of a directed graph.

    A `simple cycle`, or `elementary circuit`, is a closed path where
    no node appears twice. Two elementary circuits are distinct if they
    are not cyclic permutations of each other.

    This version uses a recursive algorithm to build a list of cycles.
    You should probably use the iterator version called simple_cycles().
    Warning: This recursive version uses lots of RAM!
    It appears in NetworkX for pedagogical value.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    A list of cycles, where each cycle is represented by a list of nodes
    along the cycle.

    Example:

    >>> edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    >>> G = nx.DiGraph(edges)
    >>> nx.recursive_simple_cycles(G)
    [[0], [2], [0, 1, 2], [0, 2], [1, 2]]

    Notes
    -----
    The implementation follows pp. 79-80 in [1]_.

    The time complexity is $O((n+e)(c+1))$ for $n$ nodes, $e$ edges and $c$
    elementary circuits.

    References
    ----------
    .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       https://doi.org/10.1137/0204007

    See Also
    --------
    simple_cycles, cycle_basis
    """

    # Jon Olav Vik, 2010-08-09
    def _unblock(thisnode):
        """Recursively unblock and remove nodes from B[thisnode]."""
        if blocked[thisnode]:
            blocked[thisnode] = False
            while B[thisnode]:
                _unblock(B[thisnode].pop())

    def circuit(thisnode, startnode, component):
        closed = False  # set to True if elementary path is closed
        path.append(thisnode)
        blocked[thisnode] = True
        for nextnode in component[thisnode]:  # direct successors of thisnode
            if nextnode == startnode:
                result.append(path[:])
                closed = True
            elif not blocked[nextnode]:
                if circuit(nextnode, startnode, component):
                    closed = True
        if closed:
            _unblock(thisnode)
        else:
            for nextnode in component[thisnode]:
                if thisnode not in B[nextnode]:  # TODO: use set for speedup?
                    B[nextnode].append(thisnode)
        path.pop()  # remove thisnode from path
        return closed

    path = []  # stack of nodes in current path
    blocked = defaultdict(bool)  # vertex: blocked from search?
    B = defaultdict(list)  # graph portions that yield no elementary circuit
    result = []  # list to accumulate the circuits found

    # Johnson's algorithm exclude self cycle edges like (v, v)
    # To be backward compatible, we record those cycles in advance
    # and then remove from subG
    for v in G:
        if G.has_edge(v, v):
            result.append([v])
            G.remove_edge(v, v)

    # Johnson's algorithm requires some ordering of the nodes.
    # They might not be sortable so we assign an arbitrary ordering.
    ordering = dict(zip(G, range(len(G))))
    for s in ordering:
        # Build the subgraph induced by s and following nodes in the ordering
        subgraph = G.subgraph(node for node in G if ordering[node] >= ordering[s])
        # Find the strongly connected component in the subgraph
        # that contains the least node according to the ordering
        strongcomp = nx.strongly_connected_components(subgraph)
        mincomp = min(strongcomp, key=lambda ns: min(ordering[n] for n in ns))
        component = G.subgraph(mincomp)
        if len(component) > 1:
            # smallest node in the component according to the ordering
            startnode = min(component, key=ordering.__getitem__)
            for node in component:
                blocked[node] = False
                B[node][:] = []
            dummy = circuit(startnode, startnode, component)
    return result


def find_cycle(G, source=None, orientation=None):
    """Returns a cycle found via depth-first traversal.

    The cycle is a list of edges indicating the cyclic path.
    Orientation of directed edges is controlled by `orientation`.

    Parameters
    ----------
    G : graph
        A directed/undirected graph/multigraph.

    source : node, list of nodes
        The node from which the traversal begins. If None, then a source
        is chosen arbitrarily and repeatedly until all edges from each node in
        the graph are searched.

    orientation : None | 'original' | 'reverse' | 'ignore' (default: None)
        For directed graphs and directed multigraphs, edge traversals need not
        respect the original orientation of the edges.
        When set to 'reverse' every edge is traversed in the reverse direction.
        When set to 'ignore', every edge is treated as undirected.
        When set to 'original', every edge is treated as directed.
        In all three cases, the yielded edge tuples add a last entry to
        indicate the direction in which that edge was traversed.
        If orientation is None, the yielded edge has no direction indicated.
        The direction is respected, but not reported.

    Returns
    -------
    edges : directed edges
        A list of directed edges indicating the path taken for the loop.
        If no cycle is found, then an exception is raised.
        For graphs, an edge is of the form `(u, v)` where `u` and `v`
        are the tail and head of the edge as determined by the traversal.
        For multigraphs, an edge is of the form `(u, v, key)`, where `key` is
        the key of the edge. When the graph is directed, then `u` and `v`
        are always in the order of the actual directed edge.
        If orientation is not None then the edge tuple is extended to include
        the direction of traversal ('forward' or 'reverse') on that edge.

    Raises
    ------
    NetworkXNoCycle
        If no cycle was found.

    Examples
    --------
    In this example, we construct a DAG and find, in the first call, that there
    are no directed cycles, and so an exception is raised. In the second call,
    we ignore edge orientations and find that there is an undirected cycle.
    Note that the second call finds a directed cycle while effectively
    traversing an undirected graph, and so, we found an "undirected cycle".
    This means that this DAG structure does not form a directed tree (which
    is also known as a polytree).

    >>> G = nx.DiGraph([(0, 1), (0, 2), (1, 2)])
    >>> nx.find_cycle(G, orientation="original")
    Traceback (most recent call last):
        ...
    networkx.exception.NetworkXNoCycle: No cycle found.
    >>> list(nx.find_cycle(G, orientation="ignore"))
    [(0, 1, 'forward'), (1, 2, 'forward'), (0, 2, 'reverse')]

    See Also
    --------
    simple_cycles
    """
    if not G.is_directed() or orientation in (None, "original"):

        def tailhead(edge):
            return edge[:2]

    elif orientation == "reverse":

        def tailhead(edge):
            return edge[1], edge[0]

    elif orientation == "ignore":

        def tailhead(edge):
            if edge[-1] == "reverse":
                return edge[1], edge[0]
            return edge[:2]

    explored = set()
    cycle = []
    final_node = None
    for start_node in G.nbunch_iter(source):
        if start_node in explored:
            # No loop is possible.
            continue

        edges = []
        # All nodes seen in this iteration of edge_dfs
        seen = {start_node}
        # Nodes in active path.
        active_nodes = {start_node}
        previous_head = None

        for edge in nx.edge_dfs(G, start_node, orientation):
            # Determine if this edge is a continuation of the active path.
            tail, head = tailhead(edge)
            if head in explored:
                # Then we've already explored it. No loop is possible.
                continue
            if previous_head is not None and tail != previous_head:
                # This edge results from backtracking.
                # Pop until we get a node whose head equals the current tail.
                # So for example, we might have:
                #  (0, 1), (1, 2), (2, 3), (1, 4)
                # which must become:
                #  (0, 1), (1, 4)
                while True:
                    try:
                        popped_edge = edges.pop()
                    except IndexError:
                        edges = []
                        active_nodes = {tail}
                        break
                    else:
                        popped_head = tailhead(popped_edge)[1]
                        active_nodes.remove(popped_head)

                    if edges:
                        last_head = tailhead(edges[-1])[1]
                        if tail == last_head:
                            break
            edges.append(edge)

            if head in active_nodes:
                # We have a loop!
                cycle.extend(edges)
                final_node = head
                break
            else:
                seen.add(head)
                active_nodes.add(head)
                previous_head = head

        if cycle:
            break
        else:
            explored.update(seen)

    else:
        assert len(cycle) == 0
        raise nx.exception.NetworkXNoCycle("No cycle found.")

    # We now have a list of edges which ends on a cycle.
    # So we need to remove from the beginning edges that are not relevant.

    for i, edge in enumerate(cycle):
        tail, head = tailhead(edge)
        if tail == final_node:
            break

    return cycle[i:]


@not_implemented_for("directed")
@not_implemented_for("multigraph")
def minimum_cycle_basis(G, weight=None):
    """Returns a minimum weight cycle basis for G

    Minimum weight means a cycle basis for which the total weight
    (length for unweighted graphs) of all the cycles is minimum.

    Parameters
    ----------
    G : NetworkX Graph
    weight: string
        name of the edge attribute to use for edge weights

    Returns
    -------
    A list of cycle lists.  Each cycle list is a list of nodes
    which forms a cycle (loop) in G. Note that the nodes are not
    necessarily returned in a order by which they appear in the cycle

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_cycle(G, [0, 1, 2, 3])
    >>> nx.add_cycle(G, [0, 3, 4, 5])
    >>> print([sorted(c) for c in nx.minimum_cycle_basis(G)])
    [[0, 1, 2, 3], [0, 3, 4, 5]]

    References:
        [1] Kavitha, Telikepalli, et al. "An O(m^2n) Algorithm for
        Minimum Cycle Basis of Graphs."
        http://link.springer.com/article/10.1007/s00453-007-9064-z
        [2] de Pina, J. 1995. Applications of shortest path methods.
        Ph.D. thesis, University of Amsterdam, Netherlands

    See Also
    --------
    simple_cycles, cycle_basis
    """
    # We first split the graph in connected subgraphs
    return sum(
        (_min_cycle_basis(G.subgraph(c), weight) for c in nx.connected_components(G)),
        [],
    )


def _min_cycle_basis(comp, weight):
    cb = []
    # We  extract the edges not in a spanning tree. We do not really need a
    # *minimum* spanning tree. That is why we call the next function with
    # weight=None. Depending on implementation, it may be faster as well
    spanning_tree_edges = list(nx.minimum_spanning_edges(comp, weight=None, data=False))
    edges_excl = [frozenset(e) for e in comp.edges() if e not in spanning_tree_edges]
    N = len(edges_excl)

    # We maintain a set of vectors orthogonal to sofar found cycles
    set_orth = [{edge} for edge in edges_excl]
    for k in range(N):
        # kth cycle is "parallel" to kth vector in set_orth
        new_cycle = _min_cycle(comp, set_orth[k], weight=weight)
        cb.append(list(set().union(*new_cycle)))
        # now update set_orth so that k+1,k+2... th elements are
        # orthogonal to the newly found cycle, as per [p. 336, 1]
        base = set_orth[k]
        set_orth[k + 1 :] = [
            orth ^ base if len(orth & new_cycle) % 2 else orth
            for orth in set_orth[k + 1 :]
        ]
    return cb


def _min_cycle(G, orth, weight=None):
    """
    Computes the minimum weight cycle in G,
    orthogonal to the vector orth as per [p. 338, 1]
    """
    T = nx.Graph()

    nodes_idx = {node: idx for idx, node in enumerate(G.nodes())}
    idx_nodes = {idx: node for node, idx in nodes_idx.items()}

    nnodes = len(nodes_idx)

    # Add 2 copies of each edge in G to T. If edge is in orth, add cross edge;
    # otherwise in-plane edge
    for u, v, data in G.edges(data=True):
        uidx, vidx = nodes_idx[u], nodes_idx[v]
        edge_w = data.get(weight, 1)
        if frozenset((u, v)) in orth:
            T.add_edges_from(
                [(uidx, nnodes + vidx), (nnodes + uidx, vidx)], weight=edge_w
            )
        else:
            T.add_edges_from(
                [(uidx, vidx), (nnodes + uidx, nnodes + vidx)], weight=edge_w
            )

    all_shortest_pathlens = dict(nx.shortest_path_length(T, weight=weight))
    cross_paths_w_lens = {
        n: all_shortest_pathlens[n][nnodes + n] for n in range(nnodes)
    }

    # Now compute shortest paths in T, which translates to cyles in G
    start = min(cross_paths_w_lens, key=cross_paths_w_lens.get)
    end = nnodes + start
    min_path = nx.shortest_path(T, source=start, target=end, weight="weight")

    # Now we obtain the actual path, re-map nodes in T to those in G
    min_path_nodes = [node if node < nnodes else node - nnodes for node in min_path]
    # Now remove the edges that occur two times
    mcycle_pruned = _path_to_cycle(min_path_nodes)

    return {frozenset((idx_nodes[u], idx_nodes[v])) for u, v in mcycle_pruned}


def _path_to_cycle(path):
    """
    Removes the edges from path that occur even number of times.
    Returns a set of edges
    """
    edges = set()
    for edge in pairwise(path):
        # Toggle whether to keep the current edge.
        edges ^= {edge}
    return edges
