#    Copyright (C) 2004-2015 by
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
"""Functions for finding and manipulating cliques.

Finding the largest clique in a graph is NP-complete problem, so most of
these algorithms have an exponential running time; for more information,
see the Wikipedia article on the clique problem [1]_.

.. [1] clique problem:: https://en.wikipedia.org/wiki/Clique_problem

"""
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

    This function returns an iterator over cliques, each of which is a
    list of nodes. The iteration is ordered by cardinality of the
    cliques: first all cliques of size one, then all cliques of size
    two, etc.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    iterator
        An iterator over cliques, each of which is a list of nodes in
        ``G``. The cliques are ordered according to size.

    Notes
    -----
    To obtain a list of all cliques, use
    `list(enumerate_all_cliques(G))`. However, be aware that in the
    worst-case, the length of this list can be exponential in the number
    of nodes in the graph (for example, when the graph is the complete
    graph). This function avoids storing all cliques in memory by only
    keeping current candidate node lists in memory during its search.

    The implementation is adapted from the algorithm by Zhang, et
    al. (2005) [1]_ to output all cliques discovered.

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Yun Zhang, Abu-Khzam, F.N., Baldwin, N.E., Chesler, E.J.,
           Langston, M.A., Samatova, N.F.,
           "Genome-Scale Computational Approaches to Memory-Intensive
           Applications in Systems Biology".
           *Supercomputing*, 2005. Proceedings of the ACM/IEEE SC 2005
           Conference, pp. 12, 12--18 Nov. 2005.
           <http://dx.doi.org/10.1109/SC.2005.29>.

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
    """Returns all maximal cliques in an undirected graph.

    For each node *v*, a *maximal clique for v* is a largest complete
    subgraph containing *v*. The largest maximal clique is sometimes
    called the *maximum clique*.

    This function returns an iterator over cliques, each of which is a
    list of nodes. It is an iterative implementation, so should not
    suffer from recursion depth issues.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    iterator
        An iterator over maximal cliques, each of which is a list of
        nodes in ``G``. The order of cliques is arbitrary.

    See Also
    --------
    find_cliques_recursive
        A recursive version of the same algorithm.

    Notes
    -----
    To obtain a list of all maximal cliques, use
    `list(find_cliques(G))`. However, be aware that in the worst-case,
    the length of this list can be exponential in the number of nodes in
    the graph (for example, when the graph is the complete graph). This
    function avoids storing all cliques in memory by only keeping
    current candidate node lists in memory during its search.

    This implementation is based on the algorithm published by Bron and
    Kerbosch (1973) [1]_, as adapted by Tomita, Tanaka and Takahashi
    (2006) [2]_ and discussed in Cazals and Karande (2008) [3]_. It
    essentially unrolls the recursion used in the references to avoid
    issues of recursion stack depth (for a recursive implementation, see
    :func:`find_cliques_recursive`).

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J.
       "Algorithm 457: finding all cliques of an undirected graph".
       *Communications of the ACM* 16, 9 (Sep. 1973), 575--577.
       <http://portal.acm.org/citation.cfm?doid=362342.362367>

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       "The worst-case time complexity for generating all maximal
       cliques and computational experiments",
       *Theoretical Computer Science*, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28--42
       <http://dx.doi.org/10.1016/j.tcs.2006.06.015>

    .. [3] F. Cazals, C. Karande,
       "A note on the problem of reporting maximal cliques",
       *Theoretical Computer Science*,
       Volume 407, Issues 1--3, 6 November 2008, Pages 564--568,
       <http://dx.doi.org/10.1016/j.tcs.2008.05.010>

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


# TODO Should this also be not implemented for directed graphs?
def find_cliques_recursive(G):
    """Returns all maximal cliques in a graph.

    For each node *v*, a *maximal clique for v* is a largest complete
    subgraph containing *v*. The largest maximal clique is sometimes
    called the *maximum clique*.

    This function returns an iterator over cliques, each of which is a
    list of nodes. It is a recursive implementation, so may suffer from
    recursion depth issues.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    iterator
        An iterator over maximal cliques, each of which is a list of
        nodes in ``G``. The order of cliques is arbitrary.

    See Also
    --------
    find_cliques
        An iterative version of the same algorithm.

    Notes
    -----
    To obtain a list of all maximal cliques, use
    `list(find_cliques_recursive(G))`. However, be aware that in the
    worst-case, the length of this list can be exponential in the number
    of nodes in the graph (for example, when the graph is the complete
    graph). This function avoids storing all cliques in memory by only
    keeping current candidate node lists in memory during its search.

    This implementation is based on the algorithm published by Bron and
    Kerbosch (1973) [1]_, as adapted by Tomita, Tanaka and Takahashi
    (2006) [2]_ and discussed in Cazals and Karande (2008) [3]_. For a
    non-recursive implementation, see :func:`find_cliques`.

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J.
       "Algorithm 457: finding all cliques of an undirected graph".
       *Communications of the ACM* 16, 9 (Sep. 1973), 575--577.
       <http://portal.acm.org/citation.cfm?doid=362342.362367>

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       "The worst-case time complexity for generating all maximal
       cliques and computational experiments",
       *Theoretical Computer Science*, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28--42
       <http://dx.doi.org/10.1016/j.tcs.2006.06.015>

    .. [3] F. Cazals, C. Karande,
       "A note on the problem of reporting maximal cliques",
       *Theoretical Computer Science*,
       Volume 407, Issues 1--3, 6 November 2008, Pages 564--568,
       <http://dx.doi.org/10.1016/j.tcs.2008.05.010>

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


# Theory has done a lot with clique graphs, but I haven't seen much on
# maximal clique graphs.
def make_max_clique_graph(G, create_using=None, name=None):
    """Returns the maximal clique graph of ``G``.

    The *maximal clique graph* of a graph `G` is the graph whose nodes
    are the maximal cliques of `G` and with an edge joining clique `C_1`
    to clique `C_2` if and only if the cliques share at least one node.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    NetworkX graph
        The maximal clique graph corresponding to ``G``.

    See also
    --------
    make_clique_bipartite

    Notes
    -----
    This is essentially a convenience function for
    ``project_up(make_clique_bipartite(G))``, but avoids having to
    perform the intermediate steps.

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
    """Returns the bipartite clique graph corresponding to ``G``.

    In the returned bipartite graph, the "bottom" nodes are the nodes of
    ``G`` and the "top" nodes represent the maximal cliques of ``G``.
    There is an edge from node *v* to clique *C* in the returned graph
    if and only if *v* is an element of *C*.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    fpos : bool
        If ``True`` or not ``None``, the returned graph will have an
        additional attribute, ``pos``, a dictionary mapping node to
        position in the Euclidean plane.


    Returns
    -------
    NetworkX graph
        A bipartite graph with nodes of ``G`` on one side and maximal
        cliques of ``G`` on the other. The returned graph has an
        additional attribute, ``node_type``, a dictionary mapping node
        to ``'Bottom'`` if it represents a node in ``G`` or ``'Top'`` if
        it represents a clique in ``G``.

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

    for v,Bvnbrs in B.adjacency():
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

    for v,Bvnbrs in B.adjacency():
       if B.node_type[v]=="Top":
          vname= -v   #Change sign of name for Top Nodes
          G.add_node(vname)
          for cv in Bvnbrs:
             # Note: -u changes the name (not Top node anymore)
             G.add_edges_from([(vname,-u) for u in B[cv] if u!=v])
    return G

def graph_clique_number(G, cliques=None):
    """Returns the clique number of the graph.

    The *clique number* of a graph is the size of the largest clique in
    the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    cliques : list
        A list of cliques, each of which is itself a list of nodes. If
        not specified, the list of all cliques will be computed, as by
        :func:`find_cliques`.

    Returns
    -------
    int
        The size of the largest clique in ``G``.

    Notes
    -----
    You should provide ``cliques`` if you have already computed the list
    of maximal cliques, in order to avoid an exponential time search for
    maximal cliques.

    """
    if cliques is None:
        cliques=find_cliques(G)
    return   max( [len(c) for c in cliques] )


def graph_number_of_cliques(G,cliques=None):
    """Returns the number of maximal cliques in the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    cliques : list
        A list of cliques, each of which is itself a list of nodes. If
        not specified, the list of all cliques will be computed, as by
        :func:`find_cliques`.

    Returns
    -------
    int
        The number of maximal cliques in ``G``.

    Notes
    -----
    You should provide ``cliques`` if you have already computed the list
    of maximal cliques, in order to avoid an exponential time search for
    maximal cliques.

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
        nodes=list(G.nodes())   # none, get entire graph

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
        nodes=list(G.nodes())   # none, get entire graph

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
        nodes=list(G.nodes())   # none, get entire graph

    if not isinstance(nodes, list):   # check for a list
        v=nodes
        # assume it is a single value
        vcliques=[c for c in cliques if v in c]
    else:
        vcliques={}
        for v in nodes:
            vcliques[v]=[c for c in cliques if v in c]
    return vcliques
