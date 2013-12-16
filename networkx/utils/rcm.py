"""
Cuthill-McKee ordering of graph nodes to produce sparse matrices
"""
#    Copyright (C) 2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    All rights reserved.
#    BSD license.
from operator import itemgetter
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg <aric.hagberg@gmail.com>'])
__all__ = ['cuthill_mckee_ordering',
           'reverse_cuthill_mckee_ordering']

def cuthill_mckee_ordering(G, start=None):
    """Generate an ordering (permutation) of the graph nodes to make 
    a sparse matrix.

    Uses the Cuthill-McKee heuristic (based on breadth-first search) [1]_.

    Parameters
    ----------
    G : graph
      A NetworkX graph 

    start : node, optional
      Start algorithm and specified node.  The node should be on the 
      periphery of the graph for best results.  

    Returns
    -------
    nodes : generator
       Generator of nodes in Cuthill-McKee ordering.

    Examples
    --------
    >>> from networkx.utils import cuthill_mckee_ordering
    >>> G = nx.path_graph(4)
    >>> rcm = list(cuthill_mckee_ordering(G))
    >>> A = nx.adjacency_matrix(G, nodelist=rcm) # doctest: +SKIP

    See Also
    --------
    reverse_cuthill_mckee_ordering
    
    Notes
    -----
    The optimal solution the the bandwidth reduction is NP-complete [2]_.

    References
    ----------
    .. [1] E. Cuthill and J. McKee.
       Reducing the bandwidth of sparse symmetric matrices,
       In Proc. 24th Nat. Conf. ACM, pages 157-172, 1969.
       http://doi.acm.org/10.1145/800195.805928
    .. [2]  Steven S. Skiena. 1997. The Algorithm Design Manual. 
       Springer-Verlag New York, Inc., New York, NY, USA.
    """
    for c in nx.connected_components(G):
        for n in connected_cuthill_mckee_ordering(G.subgraph(c), start):
            yield n

def reverse_cuthill_mckee_ordering(G, start=None):
    """Generate an ordering (permutation) of the graph nodes to make 
    a sparse matrix.

    Uses the reverse Cuthill-McKee heuristic (based on breadth-first search) 
    [1]_.

    Parameters
    ----------
    G : graph
      A NetworkX graph 

    start : node, optional
      Start algorithm and specified node.  The node should be on the 
      periphery of the graph for best results.  

    Returns
    -------
    nodes : generator
       Generator of nodes in reverse Cuthill-McKee ordering.

    Examples
    --------
    >>> from networkx.utils import reverse_cuthill_mckee_ordering
    >>> G = nx.path_graph(4)
    >>> rcm = list(reverse_cuthill_mckee_ordering(G))
    >>> A = nx.adjacency_matrix(G, nodelist=rcm) # doctest: +SKIP

    See Also
    --------
    cuthill_mckee_ordering
    
    Notes
    -----
    The optimal solution the the bandwidth reduction is NP-complete [2]_.

    References
    ----------
    .. [1] E. Cuthill and J. McKee.
       Reducing the bandwidth of sparse symmetric matrices,
       In Proc. 24th Nat. Conf. ACM, pages 157-72, 1969.
       http://doi.acm.org/10.1145/800195.805928
    .. [2]  Steven S. Skiena. 1997. The Algorithm Design Manual. 
       Springer-Verlag New York, Inc., New York, NY, USA.
    """
    return reversed(list(cuthill_mckee_ordering(G, start=start)))

def connected_cuthill_mckee_ordering(G, start=None):
    # the cuthill mckee algorithm for connected graphs
    if start is None:
        (_, start) = find_pseudo_peripheral_node_pair(G)
    yield start
    visited = set([start])
    stack = [(start, iter(G[start]))]
    while stack:
        parent,children = stack[0]
        if parent not in visited:
            yield parent
        try:
            child = next(children)
            if child not in visited:
                yield child
                visited.add(child)
                # add children to stack, sorted by degree (lowest first)
                nd = sorted(G.degree(G[child]).items(), key=itemgetter(1))
                children = (n for n,d in nd)
                stack.append((child,children))
        except StopIteration:
            stack.pop(0)

def find_pseudo_peripheral_node_pair(G, start=None):
    # helper for cuthill-mckee to find a "pseudo peripheral pair"
    # to use as good starting node 
    if start is None:
        u = next(G.nodes_iter())
    else:
        u = start
    lp = 0
    v = u 
    while True:
        spl = nx.shortest_path_length(G, v)
        l = max(spl.values())
        if l <= lp: 
            break
        lp = l
        farthest = [n for n,dist in spl.items() if dist==l]
        v, deg = sorted(G.degree(farthest).items(), key=itemgetter(1))[0]
    return u, v
    
