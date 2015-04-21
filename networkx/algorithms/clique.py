"""
=======
Cliques
=======

Find and manipulate cliques of graphs.

Note that finding the largest clique of a graph has been
shown to be an NP-complete problem; the algorithms here
could take a long time to run.

http://en.wikipedia.org/wiki/Clique_problem
"""
#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
from collections import deque
from itertools import chain, islice
try:
    from itertools import ifilter as filter
except ImportError:
    pass
import networkx
from networkx.utils.decorators import *
__author__ = """Dan Schult (dschult@colgate.edu)"""
__all__ = ['find_cliques', 'find_cliques_recursive', 'make_max_clique_graph',
           'make_clique_bipartite' ,'graph_clique_number',
           'graph_number_of_cliques', 'node_clique_number',
           'number_of_cliques', 'cliques_containing_node',
           'project_down', 'project_up', 'enumerate_all_cliques']


@not_implemented_for('directed')
def enumerate_all_cliques(G):
    """Returns all cliques in an undirected graph.

    This method returns cliques of size (cardinality)
    k = 1, 2, 3, ..., maxDegree - 1.

    Where maxDegree is the maximal degree of any node in the graph.

    Parameters
    ----------
    G: undirected graph

    Returns
    -------
    generator of lists: generator of list for each clique.

    Notes
    -----
    To obtain a list of all cliques, use
    :samp:`list(enumerate_all_cliques(G))`.

    Based on the algorithm published by Zhang et al. (2005) [1]_
    and adapted to output all cliques discovered.

    This algorithm is not applicable on directed graphs.

    This algorithm ignores self-loops and parallel edges as
    clique is not conventionally defined with such edges.

    There are often many cliques in graphs.
    This algorithm however, hopefully, does not run out of memory
    since it only keeps candidate sublists in memory and
    continuously removes exhausted sublists.

    References
    ----------
    .. [1] Yun Zhang, Abu-Khzam, F.N., Baldwin, N.E., Chesler, E.J.,
           Langston, M.A., Samatova, N.F.,
           Genome-Scale Computational Approaches to Memory-Intensive
           Applications in Systems Biology.
           Supercomputing, 2005. Proceedings of the ACM/IEEE SC 2005
           Conference, pp. 12, 12-18 Nov. 2005.
           doi: 10.1109/SC.2005.29.
           http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1559964&isnumber=33129
    """
    index = {}
    nbrs = {}
    for u in G:
        index[u] = len(index)
        # Neighbors of u that appear after u in the iteration order of G.
        nbrs[u] = {v for v in G[u] if v not in index}

    queue = deque(([u], sorted(nbrs[u], key=index.__getitem__)) for u in G)
    # Loop invariants:
    # 1. len(base) is nondecreasing.
    # 2. (base + cnbrs) is sorted with respect to the iteration order of G.
    # 3. cnbrs is a set of common neighbors of nodes in base.
    while queue:
        base, cnbrs = map(list, queue.popleft())
        yield base
        for i, u in enumerate(cnbrs):
            # Use generators to reduce memory consumption.
            queue.append((chain(base, [u]),
                          filter(nbrs[u].__contains__,
                                 islice(cnbrs, i + 1, None))))


@not_implemented_for('directed')
def find_cliques(G):
    """Search for all maximal cliques in a graph.

    Maximal cliques are the largest complete subgraph containing
    a given node.  The largest maximal clique is sometimes called
    the maximum clique.

    Returns
    -------
    generator of lists: genetor of member list for each maximal clique

    See Also
    --------
    find_cliques_recursive :
    A recursive version of the same algorithm

    Notes
    -----
    To obtain a list of cliques, use list(find_cliques(G)).

    Based on the algorithm published by Bron & Kerbosch (1973) [1]_
    as adapted by Tomita, Tanaka and Takahashi (2006) [2]_
    and discussed in Cazals and Karande (2008) [3]_.
    The method essentially unrolls the recursion used in
    the references to avoid issues of recursion stack depth.

    This algorithm is not suitable for directed graphs.

    This algorithm ignores self-loops and parallel edges as
    clique is not conventionally defined with such edges.

    There are often many cliques in graphs.  This algorithm can
    run out of memory for large graphs.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J. 1973.
       Algorithm 457: finding all cliques of an undirected graph.
       Commun. ACM 16, 9 (Sep. 1973), 575-577.
       http://portal.acm.org/citation.cfm?doid=362342.362367

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       The worst-case time complexity for generating all maximal
       cliques and computational experiments,
       Theoretical Computer Science, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28-42
       http://dx.doi.org/10.1016/j.tcs.2006.06.015

    .. [3] F. Cazals, C. Karande,
       A note on the problem of reporting maximal cliques,
       Theoretical Computer Science,
       Volume 407, Issues 1-3, 6 November 2008, Pages 564-568,
       http://dx.doi.org/10.1016/j.tcs.2008.05.010
    """
    if len(G) == 0:
        return

    adj = {u: {v for v in G[u] if v != u} for u in G}
    Q = [None]

    subg = set(G)
    cand = set(G)
    u = max(subg, key=lambda u: len(cand & adj[u]))
    ext_u = cand - adj[u]
    stack = []

    try:
        while True:
            if ext_u:
                q = ext_u.pop()
                cand.remove(q)
                Q[-1] = q
                adj_q = adj[q]
                subg_q = subg & adj_q
                if not subg_q:
                    yield Q[:]
                else:
                    cand_q = cand & adj_q
                    if cand_q:
                        stack.append((subg, cand, ext_u))
                        Q.append(None)
                        subg = subg_q
                        cand = cand_q
                        u = max(subg, key=lambda u: len(cand & adj[u]))
                        ext_u = cand - adj[u]
            else:
                Q.pop()
                subg, cand, ext_u = stack.pop()
    except IndexError:
        pass


def find_cliques_recursive(G):
    """Recursive search for all maximal cliques in a graph.

    Maximal cliques are the largest complete subgraph containing
    a given point.  The largest maximal clique is sometimes called
    the maximum clique.

    Returns
    -------
    list of lists: list of members in each maximal clique

    See Also
    --------
    find_cliques : An nonrecursive version of the same algorithm

    Notes
    -----
    Based on the algorithm published by Bron & Kerbosch (1973) [1]_
    as adapted by Tomita, Tanaka and Takahashi (2006) [2]_
    and discussed in Cazals and Karande (2008) [3]_.

    This implementation returns a list of lists each of
    which contains the members of a maximal clique.

    This algorithm ignores self-loops and parallel edges as
    clique is not conventionally defined with such edges.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J. 1973.
       Algorithm 457: finding all cliques of an undirected graph.
       Commun. ACM 16, 9 (Sep. 1973), 575-577.
       http://portal.acm.org/citation.cfm?doid=362342.362367

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       The worst-case time complexity for generating all maximal
       cliques and computational experiments,
       Theoretical Computer Science, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28-42
       http://dx.doi.org/10.1016/j.tcs.2006.06.015

    .. [3] F. Cazals, C. Karande,
       A note on the problem of reporting maximal cliques,
       Theoretical Computer Science,
       Volume 407, Issues 1-3, 6 November 2008, Pages 564-568,
       http://dx.doi.org/10.1016/j.tcs.2008.05.010
    """
    if len(G) == 0:
        return iter([])

    adj = {u: {v for v in G[u] if v != u} for u in G}
    Q = []

    def expand(subg, cand):
        u = max(subg, key=lambda u: len(cand & adj[u]))
        for q in cand - adj[u]:
            cand.remove(q)
            Q.append(q)
            adj_q = adj[q]
            subg_q = subg & adj_q
            if not subg_q:
                yield Q[:]
            else:
                cand_q = cand & adj_q
                if cand_q:
                    for clique in expand(subg_q, cand_q):
                        yield clique
            Q.pop()

    return expand(set(G), set(G))


def make_max_clique_graph(G,create_using=None,name=None):
    """ Create the maximal clique graph of a graph.

    Finds the maximal cliques and treats these as nodes.
    The nodes are connected if they have common members in
    the original graph.  Theory has done a lot with clique
    graphs, but I haven't seen much on maximal clique graphs.

    Notes
    -----
    This should be the same as make_clique_bipartite followed
    by project_up, but it saves all the intermediate steps.
    """
    cliq=list(map(set,find_cliques(G)))
    if create_using:
        B=create_using
        B.clear()
    else:
        B=networkx.Graph()
    if name is not None:
        B.name=name

    for i,cl in enumerate(cliq):
        B.add_node(i+1)
        for j,other_cl in enumerate(cliq[:i]):
            # if not cl.isdisjoint(other_cl): #Requires 2.6
            intersect=cl & other_cl
            if intersect:     # Not empty
                B.add_edge(i+1,j+1)
    return B

def make_clique_bipartite(G,fpos=None,create_using=None,name=None):
    """Create a bipartite clique graph from a graph G.

    Nodes of G are retained as the "bottom nodes" of B and
    cliques of G become "top nodes" of B.
    Edges are present if a bottom node belongs to the clique
    represented by the top node.

    Returns a Graph with additional attribute dict B.node_type
    which is keyed by nodes to "Bottom" or "Top" appropriately.

    if fpos is not None, a second additional attribute dict B.pos
    is created to hold the position tuple of each node for viewing
    the bipartite graph.
    """
    cliq=list(find_cliques(G))
    if create_using:
        B=create_using
        B.clear()
    else:
        B=networkx.Graph()
    if name is not None:
        B.name=name

    B.add_nodes_from(G)
    B.node_type={}   # New Attribute for B
    for n in B:
        B.node_type[n]="Bottom"

    if fpos:
       B.pos={}     # New Attribute for B
       delta_cpos=1./len(cliq)
       delta_ppos=1./G.order()
       cpos=0.
       ppos=0.
    for i,cl in enumerate(cliq):
       name= -i-1   # Top nodes get negative names
       B.add_node(name)
       B.node_type[name]="Top"
       if fpos:
          if name not in B.pos:
             B.pos[name]=(0.2,cpos)
             cpos +=delta_cpos
       for v in cl:
          B.add_edge(name,v)
          if fpos is not None:
             if v not in B.pos:
                B.pos[v]=(0.8,ppos)
                ppos +=delta_ppos
    return B

def project_down(B,create_using=None,name=None):
    """Project a bipartite graph B down onto its "bottom nodes".

    The nodes retain their names and are connected if they
    share a common top node in the bipartite graph.

    Returns a Graph.
    """
    if create_using:
        G=create_using
        G.clear()
    else:
        G=networkx.Graph()
    if name is not None:
        G.name=name

    for v,Bvnbrs in B.adjacency_iter():
       if B.node_type[v]=="Bottom":
          G.add_node(v)
          for cv in Bvnbrs:
             G.add_edges_from([(v,u) for u in B[cv] if u!=v])
    return G

def project_up(B,create_using=None,name=None):
    """Project a bipartite graph B down onto its "bottom nodes".

    The nodes retain their names and are connected if they
    share a common Bottom Node in the Bipartite Graph.

    Returns a Graph.
    """
    if create_using:
        G=create_using
        G.clear()
    else:
        G=networkx.Graph()
    if name is not None:
        G.name=name

    for v,Bvnbrs in B.adjacency_iter():
       if B.node_type[v]=="Top":
          vname= -v   #Change sign of name for Top Nodes
          G.add_node(vname)
          for cv in Bvnbrs:
             # Note: -u changes the name (not Top node anymore)
             G.add_edges_from([(vname,-u) for u in B[cv] if u!=v])
    return G

def graph_clique_number(G,cliques=None):
    """Return the clique number (size of the largest clique) for G.

    An optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=find_cliques(G)
    return   max( [len(c) for c in cliques] )


def graph_number_of_cliques(G,cliques=None):
    """Returns the number of maximal cliques in G.

    An optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=list(find_cliques(G))
    return   len(cliques)


def node_clique_number(G,nodes=None,cliques=None):
    """ Returns the size of the largest maximal clique containing
    each given node.

    Returns a single or list depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        if nodes is not None:
            # Use ego_graph to decrease size of graph
            if isinstance(nodes,list):
                d={}
                for n in nodes:
                    H=networkx.ego_graph(G,n)
                    d[n]=max( (len(c) for c in find_cliques(H)) )
            else:
                H=networkx.ego_graph(G,nodes)
                d=max( (len(c) for c in find_cliques(H)) )
            return d
        # nodes is None--find all cliques
        cliques=list(find_cliques(G))

    if nodes is None:
        nodes=G.nodes()   # none, get entire graph

    if not isinstance(nodes, list):   # check for a list
        v=nodes
        # assume it is a single value
        d=max([len(c) for c in cliques if v in c])
    else:
        d={}
        for v in nodes:
            d[v]=max([len(c) for c in cliques if v in c])
    return d

    # if nodes is None:                 # none, use entire graph
    #     nodes=G.nodes()
    # elif  not isinstance(nodes, list):    # check for a list
    #     nodes=[nodes]             # assume it is a single value

    # if cliques is None:
    #     cliques=list(find_cliques(G))
    # d={}
    # for v in nodes:
    #     d[v]=max([len(c) for c in cliques if v in c])

    # if nodes in G:
    #     return d[v] #return single value
    # return d


def number_of_cliques(G,nodes=None,cliques=None):
    """Returns the number of maximal cliques for each node.

    Returns a single or list depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=list(find_cliques(G))

    if nodes is None:
        nodes=G.nodes()   # none, get entire graph

    if not isinstance(nodes, list):   # check for a list
        v=nodes
        # assume it is a single value
        numcliq=len([1 for c in cliques if v in c])
    else:
        numcliq={}
        for v in nodes:
            numcliq[v]=len([1 for c in cliques if v in c])
    return numcliq


def cliques_containing_node(G,nodes=None,cliques=None):
    """Returns a list of cliques containing the given node.

    Returns a single list or list of lists depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques=list(find_cliques(G))

    if nodes is None:
        nodes=G.nodes()   # none, get entire graph

    if not isinstance(nodes, list):   # check for a list
        v=nodes
        # assume it is a single value
        vcliques=[c for c in cliques if v in c]
    else:
        vcliques={}
        for v in nodes:
            vcliques[v]=[c for c in cliques if v in c]
    return vcliques
