# -*- encoding: utf-8 -*-
#    Copyright (C) 2010-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
"""Functions for finding cycles in a graph."""

from collections import defaultdict

try:
    import scipy as sp
except:
    is_scipy_available = False
else:
    is_scipy_available = True

import networkx as nx
from networkx.algorithms.traversal.edgedfs import helper_funcs, edge_dfs
from networkx.utils import not_implemented_for

__all__ = ['chords', 'cycle_basis', 'cycle_basis_matrix', 'find_cycle',
           'recursive_simple_cycles', 'simple_cycles']

__author__ = "\n".join(['Jon Olav Vik <jonovik@gmail.com>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Aric Hagberg <hagberg@lanl.gov>',
                        'JuanPi Carbajal <ajuanpi+dev@gmail.com>',
                        'Jeffrey Finkelstein <jeffrey.finkelstein@gmail.com>'])


@not_implemented_for('directed')
def cycle_basis(G, root=None, T=None):
    """Returns a list of cycles that form a basis for the cycle space of
    ``G``.

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
    >>> nx.cycle_basis(G, 0)
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


@not_implemented_for('undirected')
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
    >>> G = nx.DiGraph([(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)])
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

    The time complexity is `O((n+e)(c+1))` for `n` nodes, `e` edges and `c`
    elementary circuits.

    References
    ----------
    .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       http://dx.doi.org/10.1137/0204007
    .. [2] Enumerating the cycles of a digraph: a new preprocessing strategy.
       G. Loizou and P. Thanish, Information Sciences, v. 27, 163-182, 1982.
    .. [3] A search strategy for the elementary cycles of a directed graph.
       J.L. Szwarcfiter and P.E. Lauer, BIT NUMERICAL MATHEMATICS,
       v. 16, no. 2, 192-204, 1976.

    See Also
    --------
    cycle_basis
    """
    def _unblock(thisnode,blocked,B):
        stack=set([thisnode])
        while stack:
            node=stack.pop()
            if node in blocked:
                blocked.remove(node)
                stack.update(B[node])
                B[node].clear()

    # Johnson's algorithm requires some ordering of the nodes.
    # We assign the arbitrary ordering given by the strongly connected comps
    # There is no need to track the ordering as each node removed as processed.
    subG = type(G)(G.edges()) # save the actual graph so we can mutate it here
                              # We only take the edges because we do not want to
                              # copy edge and node attributes here.
    sccs = list(nx.strongly_connected_components(subG))
    while sccs:
        scc=sccs.pop()
        # order of scc determines ordering of nodes
        startnode = scc.pop()
        # Processing node runs "circuit" routine from recursive version
        path=[startnode]
        blocked = set() # vertex: blocked from search?
        closed = set() # nodes involved in a cycle
        blocked.add(startnode)
        B=defaultdict(set) # graph portions that yield no elementary circuit
        stack=[ (startnode,list(subG[startnode])) ]  # subG gives component nbrs
        while stack:
            thisnode,nbrs = stack[-1]
            if nbrs:
                nextnode = nbrs.pop()
#                    print thisnode,nbrs,":",nextnode,blocked,B,path,stack,startnode
#                    f=raw_input("pause")
                if nextnode == startnode:
                    yield path[:]
                    closed.update(path)
#                        print "Found a cycle",path,closed
                elif nextnode not in blocked:
                    path.append(nextnode)
                    stack.append( (nextnode,list(subG[nextnode])) )
                    closed.discard(nextnode)
                    blocked.add(nextnode)
                    continue
            # done with nextnode... look for more neighbors
            if not nbrs:  # no more nbrs
                if thisnode in closed:
                    _unblock(thisnode,blocked,B)
                else:
                    for nbr in subG[thisnode]:
                        if thisnode not in B[nbr]:
                            B[nbr].add(thisnode)
                stack.pop()
#                assert path[-1]==thisnode
                path.pop()
        # done processing this node
        subG.remove_node(startnode)
        H=subG.subgraph(scc)  # make smaller to avoid work in SCC routine
        sccs.extend(list(nx.strongly_connected_components(H)))


@not_implemented_for('undirected')
def recursive_simple_cycles(G):
    """Find simple cycles (elementary circuits) of a directed graph.

    A `simple cycle`, or `elementary circuit`, is a closed path where
    no node appears twice. Two elementary circuits are distinct if they
    are not cyclic permutations of each other.

    This version uses a recursive algorithm to build a list of cycles.
    You should probably use the iterator version called simple_cycles().
    Warning: This recursive version uses lots of RAM!

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    A list of cycles, where each cycle is represented by a list of nodes
    along the cycle.

    Example:

    >>> G = nx.DiGraph([(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)])
    >>> nx.recursive_simple_cycles(G)
    [[0], [0, 1, 2], [0, 2], [1, 2], [2]]

    See Also
    --------
    cycle_basis (for undirected graphs)

    Notes
    -----
    The implementation follows pp. 79-80 in [1]_.

    The time complexity is `O((n+e)(c+1))` for `n` nodes, `e` edges and `c`
    elementary circuits.

    References
    ----------
    .. [1] Finding all the elementary circuits of a directed graph.
       D. B. Johnson, SIAM Journal on Computing 4, no. 1, 77-84, 1975.
       http://dx.doi.org/10.1137/0204007

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
        closed = False # set to True if elementary path is closed
        path.append(thisnode)
        blocked[thisnode] = True
        for nextnode in component[thisnode]: # direct successors of thisnode
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
                if thisnode not in B[nextnode]: # TODO: use set for speedup?
                    B[nextnode].append(thisnode)
        path.pop() # remove thisnode from path
        return closed

    path = [] # stack of nodes in current path
    blocked = defaultdict(bool) # vertex: blocked from search?
    B = defaultdict(list) # graph portions that yield no elementary circuit
    result = [] # list to accumulate the circuits found
    # Johnson's algorithm requires some ordering of the nodes.
    # They might not be sortable so we assign an arbitrary ordering.
    ordering=dict(zip(G,range(len(G))))
    for s in ordering:
        # Build the subgraph induced by s and following nodes in the ordering
        subgraph = G.subgraph(node for node in G
                              if ordering[node] >= ordering[s])
        # Find the strongly connected component in the subgraph
        # that contains the least node according to the ordering
        strongcomp = nx.strongly_connected_components(subgraph)
        mincomp=min(strongcomp,
                    key=lambda nodes: min(ordering[n] for n in nodes))
        component = G.subgraph(mincomp)
        if component:
            # smallest node in the component according to the ordering
            startnode = min(component,key=ordering.__getitem__)
            for node in component:
                blocked[node] = False
                B[node][:] = []
            dummy=circuit(startnode, startnode, component)
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
    """
    Returns the edges of a cycle found via a directed, depth-first traversal.

    Parameters
    ----------
    G : graph
        A directed/undirected graph/multigraph.

    source : node, list of nodes
        The node from which the traversal begins. If None, then a source
        is chosen arbitrarily and repeatedly until all edges from each node in
        the graph are searched.

    orientation : 'original' | 'reverse' | 'ignore'
        For directed graphs and directed multigraphs, edge traversals need not
        respect the original orientation of the edges. When set to 'reverse',
        then every edge will be traversed in the reverse direction. When set to
        'ignore', then each directed edge is treated as a single undirected
        edge that can be traversed in either direction. For undirected graphs
        and undirected multigraphs, this parameter is meaningless and is not
        consulted by the algorithm.

    Returns
    -------
    edges : directed edges
        A list of directed edges indicating the path taken for the loop. If
        no cycle is found, then an exception is raised. For graphs, an
        edge is of the form `(u, v)` where `u` and `v` are the tail and head
        of the edge as determined by the traversal. For multigraphs, an edge is
        of the form `(u, v, key)`, where `key` is the key of the edge. When the
        graph is directed, then `u` and `v` are always in the order of the
        actual directed edge. If orientation is 'ignore', then an edge takes
        the form `(u, v, key, direction)` where direction indicates if the edge
        was followed in the forward (tail to head) or reverse (head to tail)
        direction. When the direction is forward, the value of `direction`
        is 'forward'. When the direction is reverse, the value of `direction`
        is 'reverse'.
        
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

    >>> import networkx as nx
    >>> G = nx.DiGraph([(0,1), (0,2), (1,2)])
    >>> try:
    ...    find_cycle(G, orientation='original')
    ... except:
    ...    pass
    ...
    >>> list(find_cycle(G, orientation='ignore'))
    [(0, 1, 'forward'), (1, 2, 'forward'), (0, 2, 'reverse')]

    """
    out_edge, key, tailhead = helper_funcs(G, orientation)

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
        previous_node = None
        for edge in edge_dfs(G, start_node, orientation):
            # Determine if this edge is a continuation of the active path.
            tail, head = tailhead(edge)
            if previous_node is not None and tail != previous_node:
                # This edge results from backtracking.
                # Pop until we get a node whose head equals the current tail.
                # So for example, we might have:
                #  (0,1), (1,2), (2,3), (1,4)
                # which must become:
                #  (0,1), (1,4)
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
            elif head in explored:
                # Then we've already explored it. No loop is possible.
                break
            else:
                seen.add(head)
                active_nodes.add(head)
                previous_node = head

        if cycle:
            break
        else:
            explored.update(seen)

    else:
        assert(len(cycle) == 0)
        raise nx.exception.NetworkXNoCycle('No cycle found.')

    # We now have a list of edges which ends on a cycle.
    # So we need to remove from the beginning edges that are not relevant.

    for i, edge in enumerate(cycle):
        tail, head = tailhead(edge)
        if tail == final_node:
            break

    return cycle[i:]
