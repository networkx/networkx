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
import networkx as nx
from networkx.utils import *
from collections import defaultdict

__all__ = ['cycle_basis','cycle_basis_matrix','simple_cycles','recursive_simple_cycles','chords']
__author__ = "\n".join(['Jon Olav Vik <jonovik@gmail.com>',
                        'Dan Schult <dschult@colgate.edu>',
                        'Aric Hagberg <hagberg@lanl.gov>',
                        'JuanPi Carbajal <ajuanpi+dev@gmail.com>'])

@not_implemented_for('directed')
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
    >>> G.add_cycle([0,1,2,3])
    >>> G.add_cycle([0,3,4,5])
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
    cycles = []
    # Add all cycles due to multiple edges between nodes
    if G.is_multigraph():
      C,T   = chords(G)
      for e in C.edges_iter():
          if T.has_edge(*e) or T.has_edge(*e[::-1]):
              cycles.append(list(e))
      # Make G a graph so the original algorithm works
      G = nx.Graph(G)

    gnodes = set(G.nodes())
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

def cycle_basis_matrix(G, sparse=False):
    """Return a the matrix describing the fundamental cycles in G.
     If G is not oriented and arbitrary orientation is taken.

    Parameters
    ----------
    G : NetworkX Graph.
    sparse : Boolean, optional. Not used.
    
    Returns
    -------
    M : Matrix (int8) of the fundametal cycles. The matrix
    is of size n-by-m where n is the numer of edges in the
    graph and m is the number of fundamental cycles (as given
    by cycle_basis). A nonzero entry (i,j) implies that the
    edge i is in cycle j. The sign of the entry indicates in
    which direction it should be followed to go around the cycle:
    a negative netry means opposite to the direction of that edge
    in G.
    
    
    Notes
    -----
    This function needs scipy to work.
    TODO: Return a sparse matrix if required.

    See Also
    --------
    cycle_basis
    """
    import scipy as np

    C,T  = chords(G)
    nrow = len(G.edges())
    ncol = len(C.edges())
    
    if G.is_directed():
        raise nx.NetworkXNotImplemented('not implemented for directed type')
    
    if sparse:
        raise nx.NetworkXNotImplemented('sparse matrix not implemented yet.')
    else:
        M = np.zeros([nrow,ncol],dtype=np.int8)

    if G.is_multigraph():
        Cedges_iter = C.edges_iter(keys=True)

        Gedges = G.edges(keys=True)
        Tedges = T.edges(keys=True)
    else:
        Cedges_iter = C.edges_iter()
        Gedges = G.edges()
        Tedges = T.edges()

    for col, e in enumerate(Cedges_iter):
        row = Gedges.index(e)
        M[row,col]  = 1

        edge     = e[:2]        # nodes of the edge in given order
        edge_inv = e[:2][::-1]  # nodes of the edge in reverse order
        try:
            einT  = T.edges().index(edge)
            # The edge is in the tree with the same orientation, hence invert it
            row2        = Gedges.index(Tedges[einT])
            M[row2,col] = -1
        except ValueError:
            try:
                ieinT = T.edges().index(edge_inv)
                # The edge is in the tree with the opposite orientation, hence leave it
                row2        = Gedges.index(Tedges[ieinT])
                M[row2,col] = 1
            except ValueError:
                tmp = T.edges()
                tmp.append(edge)
                cyc = cycle_basis(nx.Graph(tmp))[0]
                cyc_e = []

                for idx,node in enumerate(cyc):
                    if  idx < len(cyc)-1:
                        cyc_e.append((node, cyc[idx+1]))
                    else:
                        cyc_e.append((node, cyc[0]))

                if edge_inv in cyc_e:
                    # The chord is in the cycle with the opposite orientation
                    # invert all edges of the cycle
                    cyc_e = [i[::-1] for i in cyc_e]

                elif edge not in cyc_e:
                    raise NameError('Something went wrong! The edge {} is not in cycle {}'.format(e,cyc))

                cyc_e.remove(edge)
                for ce in cyc_e:
                    try:
                        einT  = T.edges().index(ce)
                        # The edge is in the tree with the same orientation
                        row2        = Gedges.index(Tedges[einT])
                        M[row2,col] = 1
                    except ValueError:
                        ieinT = T.edges().index(ce[::-1])
                        # The edge is in the tree with the opposite orientation
                        row2        = Gedges.index(Tedges[ieinT])
                        M[row2,col] = -1

    return M


@not_implemented_for('undirected')
def simple_cycles(G):
    """Find simple cycles (elementary circuits) of a directed graph.

    An simple cycle, or elementary circuit, is a closed path where no
    node appears twice, except that the first and last node are the same.
    Two elementary circuits are distinct if they are not cyclic permutations
    of each other.

    This is a nonrecursive, iterator/generator version of Johnson's
    algorithm [1]_.  There may be better algorithms for some cases [2]_ [3]_.

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    cycle_generator: generator
       A generator that produces elementary cycles of the graph.  Each cycle is
       a list of nodes with the first and last nodes being the same.

    Examples
    --------
    >>> G = nx.DiGraph([(0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2)])
    >>> list(nx.simple_cycles(G))
    [[2], [2, 1], [2, 0], [2, 0, 1], [0]]

    Notes
    -----
    The implementation follows pp. 79-80 in [1]_.

    The time complexity is O((n+e)(c+1)) for n nodes, e edges and c
    elementary circuits.

    To filter the cycles so that they don't include certain nodes or edges,
    copy your graph and eliminate those nodes or edges before calling.
    >>> copyG = G.copy()
    >>> copyG.remove_nodes_from([1])
    >>> copyG.remove_edges_from([(0,1)])
    >>> list(nx.simple_cycles(copyG))
    [[2], [2, 0], [0]]

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
    subG = type(G)(G.edges_iter()) # save the actual graph so we can mutate it here
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

    A simple cycle, or elementary circuit, is a closed path where no
    node appears twice, except that the first and last node are the same.
    Two elementary circuits are distinct if they are not cyclic permutations
    of each other.

    This version uses a recursive algorithm to build a list of cycles.
    You should probably use the iterator version caled simple_cycles().
    Warning: This recursive version uses lots of RAM!

    Parameters
    ----------
    G : NetworkX DiGraph
       A directed graph

    Returns
    -------
    A list of circuits, where each circuit is a list of nodes, with the first
    and last node being the same.

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

    The time complexity is O((n+e)(c+1)) for n nodes, e edges and c
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

def chords(G):
    """Return a new graph that contains the edges that are the chords of G.

        The chords are all the edges that are not in a spanning three of G.

    Parameters
    ----------
    G : graph
       A NetworkX graph.

    Returns
    -------
    C : A new graph with the chords of G.
    T : The spanning tree from which C was calculated.

    Raises
    ------
    NetworkXError
        The algorithm does not support directed graphs. 
        If the input graph directed, a NetworkXError is raised.
        To run this algorithm on a directed graph, first convert it
        to undirected.

    Examples
    --------
    >>> import networkx as nx
    >>> e=[(1,2),(1,3),(2,3),(2,4),(3,4),(3,5),(3,6),(4,5),(4,6),(5,6)]
    >>> G=nx.Graph(e)
    >>> C,T = nx.chords(G)

    Notes
    -----
    The routine is a direct implementation of the definition of chords.
    It constructs the spanning minimum spanning tree of G and then removes
    the edges in that tree from G.
    """
  
    # Cast G to undirected and then T back to the same type as G
    # Multigraphs keys get lost in the call to spanning_tree so we have to add them.
    
    if G.is_directed():
        # Remove directionality
        if G.is_multigraph():
            # All keys lost
            T = nx.minimum_spanning_tree(nx.MultiGraph(G))
        else:
            T = nx.DiGraph(nx.minimum_spanning_tree(nx.Graph(G)))
    else:
        # All keys lost
        T = nx.minimum_spanning_tree(G)
    
    C = G.copy()
    # Recover keys and make chords
    if G.is_multigraph():
        Tedges=T.edges() 
        to_add=[]
        for e in G.edges_iter(keys=True, data=True):
            if e[:2] in Tedges:
              to_add.append(e)
              Tedges.pop(Tedges.index(e[:2]))
            if not Tedges:
                break
        T = nx.MultiGraph(to_add)
        # Difference to keep attributes ad keys
        C.remove_edges_from ([n for n in G.edges_iter(keys=True) if n in T.edges_iter(keys=True)])
    else:
        C.remove_edges_from ([n for n in G.edges_iter() if n in T.edges_iter()])
    

    return C,T

