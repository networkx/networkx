"""
========================
Cycle finding algorithms
========================
"""

from collections import defaultdict

try:
    import scipy as sp
except:
    is_scipy_available = False
else:
    is_scipy_available = True

import networkx as nx
from networkx.utils import not_implemented_for, pairwise

__all__ = [
    "chords",
    "cycle_basis",
    "cycle_basis_matrix",
    "simple_cycles",
    "recursive_simple_cycles",
    "find_cycle",
    "minimum_cycle_basis",
]


@not_implemented_for('directed')
def cycle_basis(G, root=None, T=None):
    """Returns a list of cycles which form a basis for cycles of G.

    The `cycle space`_ of a graph is the vector space of its Eulerian
    subgraphs, with vector addition defined by symmetric difference of
    the subgraphs. A `cycle basis`_ is a basis for this vector space.
    It is a minimal collection of cycles such that any cycle in the
    network can be written as a "sum" (in the sense of symmetric
    difference, as stated above) of cycles in the basis.

    Cycle bases are useful when considering a graph as an electrical
    circuit that complies with `Kirchhoff's circuit laws`_.

    .. _cycle space: https://en.wikipedia.org/wiki/Cycle_space
    .. _cycle basis: https://en.wikipedia.org/wiki/Cycle_basis
    .. _Kirchhoff's circuit laws: https://en.wikipedia.org/wiki/Kirchhoff%27s_circuit_laws

    Parameters
    ----------
    G : NetworkX Graph

    root : node, optional
        A starting node to use when computing the basis.

    T : NetworkX graph, optional
        Use this particular spanning tree when computing the cycles
        induced by parallel edges joining pairs of nodes in a
        multigraph. This must be a NetworkX graph object representing a
        spanning tree of the graph ``G``. If not provided, a minimum
        spanning tree will be computed.

        This argument is ignored if ``G`` is not a multigraph.

    Returns
    -------
    list
        A list of cycles, each of which is itself a list of nodes
        representing a cycle in the graph.

    Examples
    --------
    >>> G = nx.Graph()
    >>> nx.add_cycle(G, [0, 1, 2, 3])
    >>> nx.add_cycle(G, [0, 3, 4, 5])
    >>> print(nx.cycle_basis(G, 0))
    [[3, 4, 5, 0], [1, 2, 3, 0]]

    Notes
    -----
    This implementation is adapted from algorithm CACM 491 [1]_.

    References
    ----------
    .. [1] Paton, K.
           "An algorithm for finding a fundamental set of cycles of a graph."
           *Communications of the ACM* 12, 9 (Sept. 1969), 514–518.

    See Also
    --------
    simple_cycles

    """
    cycles = []
    # Add all cycles due to multiple edges between nodes.
    if G.is_multigraph():
        C, T = chords(G, T=T, output_tree=True)
        cycles = [[u, v] for u, v in C.edges() if v in T[u] or u in T[v]]
        # Make G a graph so that the original algorithm works.
        G = nx.Graph(G)

    gnodes = set(G)
    while gnodes:
        if root is None:
            root = gnodes.pop()
        # TODO stack should use deque
        stack = [root]
        pred = {root: root}
        used = {root: set()}
        # Walk the spanning tree, finding cycles.
        while stack:
            # Use last-in so that cycles are easier to find.
            z = stack.pop()
            zused = used[z]
            for nbr in G[z]:
                # If this is a node we have not already seen...
                if nbr not in used:
                    pred[nbr] = z
                    stack.append(nbr)
                    used[nbr] = set([z])
                # If this is a self-loop, immediately add the singleton
                # list of this vertex as a cycle.
                elif nbr == z:
                    cycles.append([z])
                # If we have found a cycle...
                elif nbr not in zused:
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


@not_implemented_for('directed')
def cycle_basis_matrix(G, T=None):
    """Returns the matrix describing the fundamental cycles in ``G``.

    If ``G`` is not a directed graph, an arbitrary orientation of the edges is selected.

    Parameters
    ----------
    G : NetworkX Graph
        An instance of :class:`networkx.Graph` or :class:`networkx.MultiGraph`.

    T : NetworkX graph, optional
        A spanning tree for the graph ``G``. If this argument is not ``None``,
        the cycle basis whose matrix will be returned will be the set of
        `fundamental cycles`_ with respect to the tree ``T``. If this is not specified, an
        arbitrary minimum spanning tree will be used.

    .. _fundamental cycles: https://en.wikipedia.org/wiki/Spanning_tree#Fundamental_cycles

    Returns
    -------
    NumPy array with dtype ``int8``
        Returns a NumPy array of shape (*n*, *m*) and dtype ``int8``,
        where *n* is the number of edges in the graph and *m* is the
        number of fundamental cycles (as given by
        :func:`cycle_basis`). If entry (*i*, *j*) is nonzero, then edge
        *i* is in cycle *j* in the cycle basis. The sign of the entry
        indicates the orientation of the edge in the cycle: a negative
        entry means opposite to the direction of that edge in ``G``.

    Notes
    -----
    This function requires SciPy.

    See Also
    --------
    cycle_basis

    """
    if not is_scipy_available:
        raise nx.NetworkXError('This function requires SciPy:'
                               ' https://www.scipy.org/')
    C, T = chords(G, T=T, output_tree=True)
    nrow = len(G.edges())
    ncol = len(C.edges())
    M = sp.zeros([nrow, ncol], dtype=sp.int8)
    if G.is_multigraph():
        Cedges = C.edges(keys=True)

        Gedges = G.edges(keys=True)
        Tedges = T.edges(keys=True)
    else:
        Cedges = C.edges()
        Gedges = G.edges()
        Tedges = T.edges()

    for col, e in enumerate(Cedges):
        row = Gedges.index(e)
        M[row, col] = 1

        # Get the edge endpoints in the default order and in the reverse order.
        edge = e[:2]
        edge_inv = e[:2][::-1]
        try:
            einT = T.edges().index(edge)
            # The edge is in the tree with the same orientation, hence
            # invert it.
            row2 = Gedges.index(Tedges[einT])
            M[row2, col] = -1
        except ValueError:
            try:
                ieinT = T.edges().index(edge_inv)
                # The edge is in the tree with the opposite orientation,
                # hence leave it.
                row2 = Gedges.index(Tedges[ieinT])
                M[row2, col] = 1
            except ValueError:
                tmp = T.edges()
                tmp.append(edge)
                cyc = cycle_basis(nx.Graph(tmp))[0]
                cyc_e = []

                for idx, node in enumerate(cyc):
                    if idx < len(cyc)-1:
                        cyc_e.append((node, cyc[idx + 1]))
                    else:
                        cyc_e.append((node, cyc[0]))

                if edge_inv in cyc_e:
                    # The chord is in the cycle with the opposite orientation,
                    # so invert all edges of the cycle.
                    cyc_e = [i[::-1] for i in cyc_e]
                elif edge not in cyc_e:
                    raise NameError('Something went wrong! The edge {} is not'
                                    ' in cycle {}'.format(e, cyc))

                cyc_e.remove(edge)
                for ce in cyc_e:
                    try:
                        einT = T.edges().index(ce)
                        # The edge is in the tree with the same orientation.
                        row2 = Gedges.index(Tedges[einT])
                        M[row2, col] = 1
                    except ValueError:
                        ieinT = T.edges().index(ce[::-1])
                        # The edge is in the tree with the opposite
                        # orientation.
                        row2 = Gedges.index(Tedges[ieinT])
                        M[row2, col] = -1

    return M


@not_implemented_for("undirected")
def simple_cycles(G):
    """Find simple cycles (elementary circuits) of a directed graph.

    A `simple cycle`, or `elementary circuit`, is a closed path where
    no node appears twice. Two elementary circuits are distinct if they
    are not cyclic permutations of each other.

    This is a nonrecursive, iterator/generator version of Johnson's
    algorithm [1]_.  There may be better algorithms for some cases [2]_ [3]_.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    cycle_generator: generator
       A generator that produces elementary cycles of the graph.
       Each cycle is represented by a list of nodes along the cycle.

    Examples
    --------
    >>> edges = [(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)]
    >>> G = nx.DiGraph(edges)
    >>> len(list(nx.simple_cycles(G)))
    5

    To filter the cycles so that they don't include certain nodes or edges,
    copy your graph and eliminate those nodes or edges before calling

    >>> copyG = G.copy()
    >>> copyG.remove_nodes_from([1])
    >>> copyG.remove_edges_from([(0, 1)])
    >>> len(list(nx.simple_cycles(copyG)))
    3


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
    .. [2] Enumerating the cycles of a digraph: a new preprocessing strategy.
       G. Loizou and P. Thanish, Information Sciences, v. 27, 163-182, 1982.
    .. [3] A search strategy for the elementary cycles of a directed graph.
       J.L. Szwarcfiter and P.E. Lauer, BIT NUMERICAL MATHEMATICS,
       v. 16, no. 2, 192-204, 1976.

    See Also
    --------
    cycle_basis
    """

    def _unblock(thisnode, blocked, B):
        stack = {thisnode}
        while stack:
            node = stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    # Also we save the actual graph so we can mutate it. We only take the
    # edges because we do not want to copy edge and node attributes here.
    subG = type(G)(G.edges())
    sccs = [scc for scc in nx.strongly_connected_components(subG) if len(scc) > 1]

    # Johnson's algorithm exclude self cycle edges like (v, v)
    # To be backward compatible, we record those cycles in advance
    # and then remove from subG
    for v in subG:
        if subG.has_edge(v, v):
            yield [v]
            subG.remove_edge(v, v)

    while sccs:
        scc = sccs.pop()
        sccG = subG.subgraph(scc)
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path = [startnode]
        blocked = set()  # vertex: blocked from search?
        closed = set()  # nodes involved in a cycle
        blocked.add(startnode)
        B = defaultdict(set)  # graph portions that yield no elementary circuit
        stack = [(startnode, list(sccG[startnode]))]  # sccG gives comp nbrs
        while stack:
            thisnode, nbrs = stack[-1]
            if nbrs:
                nextnode = nbrs.pop()
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
                #                        print "Found a cycle", path, closed
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append((nextnode, list(sccG[nextnode])))
                    closed.discard(nextnode)
                    blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode, blocked, B)
                else:
                    for nbr in sccG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
                #                assert path[-1] == thisnode
                path.pop()
        # done processing this node
        H = subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(scc for scc in nx.strongly_connected_components(H) if len(scc) > 1)


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


# TODO Does this really need to return a graph? Can it just return the edges?
def chords(G, T=None, output_tree=False):
    """Returns a copy of the subgraph induced by edges in ``G`` not in
    the spanning tree ``T``.

    This function returns a new graph object.

    Parameters
    ----------
    G : NetworkX graph

    T : NetworkX graph
        A spanning tree for the graph ``G``, for example, as computed by
        :func:`networkx.minimum_spanning_tree`.

    output_tree : bool
        If this is ``False`` (the default), then the function returns
        only the chords. If this is ``True``, then the function returns
        the chords and the spanning tree from which the chords were
        computed.

    Returns
    -------
    NetworkX graph or a pair of NetworkX graphs

        If ``output_tree`` is ``False`` (the default) then this function
        returns a graph containing only the chords of ``G`` with respect
        to the spanning tree ``T`` (or a minimum spanning tree if ``T``
        is not specified). The type of the graph is the same as the type
        of ``G``.

        If ``output_tree`` is ``True``, then this function returns a
        pair whose left element is the graph of chords as described
        above and whose right element is the spanning tree used to
        compute those chords. If ``T`` is provided, it is returned
        unmodified.

    Examples
    --------
    If no spanning tree is provided, a minimum spanning tree is chosen
    for you::

        >>> import networkx as nx
        >>> e = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (3, 5), (3, 6),
        ...      (4, 5), (4, 6), (5, 6)]
        >>> G = nx.Graph(e)
        >>> C, T = nx.chords(G, output_tree=True)
        >>> sorted(C.edges())
        [(2, 3), (3, 4), (4, 5), (4, 6), (5, 6)]
        >>> sorted(T.edges())
        [(1, 2), (1, 3), (2, 4), (3, 5), (3, 6)]

    Notes
    -----
    This is a direct implementation of the definition of chords.  It
    constructs the minimum spanning tree of ``G`` and then removes the
    edges in that tree from ``G``.

    """
    if T is None:
        T = nx.minimum_spanning_tree(G, as_multigraph=G.is_multigraph())
    G_edges = G.edges(keys=True) if G.is_multigraph() else G.edges()
    C = G.edge_subgraph(e for e in G_edges if not T.has_edge(*e))
    return (C, T) if output_tree else C


def find_cycle(G, source=None, orientation='original'):
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
    # We first split the graph in commected subgraphs
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
