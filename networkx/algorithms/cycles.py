"""
========================
Cycle finding algorithms
========================
"""
#    Copyright (C) 2010-2012 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

from collections import defaultdict

import networkx as nx
from networkx.utils import *
from networkx.algorithms.traversal.edgedfs import helper_funcs, edge_dfs

__all__ = [
    'cycle_basis','simple_cycles','recursive_simple_cycles', 'find_cycle'
]

__author__ = "\n".join(['Jon Olav Vik <jonovik@gmail.com>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Aric Hagberg <hagberg@lanl.gov>'])

@not_implemented_for('directed')
@not_implemented_for('multigraph')
def cycle_basis(G,root=None):
    """ Returns a list of cycles which form a basis for cycles of G.

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
    >>> G=nx.Graph()
    >>> nx.add_cycle(G, [0, 1, 2, 3])
    >>> nx.add_cycle(G, [0, 3, 4, 5])
    >>> print(nx.cycle_basis(G,0))
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
    gnodes=set(G.nodes())
    cycles=[]
    while gnodes:  # loop over connected components
        if root is None:
            root=gnodes.pop()
        stack=[root]
        pred={root:root}
        used={root:set()}
        while stack:  # walk the spanning tree finding cycles
            z=stack.pop()  # use last-in so cycles easier to find
            zused=used[z]
            for nbr in G[z]:
                if nbr not in used:   # new node
                    pred[nbr]=z
                    stack.append(nbr)
                    used[nbr]=set([z])
                elif nbr == z:        # self loops
                    cycles.append([z])
                elif nbr not in zused:# found a cycle
                    pn=used[nbr]
                    cycle=[nbr,z]
                    p=pred[z]
                    while p not in pn:
                        cycle.append(p)
                        p=pred[p]
                    cycle.append(p)
                    cycles.append(cycle)
                    used[nbr].add(z)
        gnodes-=set(pred)
        root=None
    return cycles


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

    def prune(edges, active_nodes):
        # This edge results from backtracking.
        # Pop until we get a node whose head equals the current tail.
        # So for example, we might have:
        #  [(0,1), (1,2), (2,3)], (1,4)
        # which must become:
        #  [(0,1)], (1,4)
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
                previous_head = tailhead(edges[-1])[1]
                if tail == previous_head:
                    break
            else:
                previous_head = None
        return edges, active_nodes, previous_head

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

        for edge in edge_dfs(G, start_node, orientation):
            # Determine if this edge is a continuation of the active path.
            tail, head = tailhead(edge)
            if previous_head is not None and tail != previous_head:
                edges, active_nodes, previous_head = prune(edges, active_nodes)
            edges.append(edge)

            if head in active_nodes:
                # We have a loop!
                cycle.extend(edges)
                final_node = head
                break
            else:
                previous_head = head
                seen.add(head)
                active_nodes.add(head)
                if head in explored:
                    edges, active_nodes, previous_head = prune(edges, active_nodes)

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

