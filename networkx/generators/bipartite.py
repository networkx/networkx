# -*- coding: utf-8 -*-
"""
Generators and functions for bipartite graphs.

"""
#    Copyright (C) 2006-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import math
import random
import networkx 
from functools import reduce
import networkx as nx
__author__ = """\n""".join(['Aric Hagberg (hagberg@lanl.gov)',
                            'Pieter Swart (swart@lanl.gov)',
                            'Dan Schult(dschult@colgate.edu)'])
__all__=['bipartite_configuration_model',
         'bipartite_havel_hakimi_graph',
         'bipartite_reverse_havel_hakimi_graph',
         'bipartite_alternating_havel_hakimi_graph',
         'bipartite_preferential_attachment_graph',
         'bipartite_random_regular_graph',
         'bipartite_random_graph',
         ]


def bipartite_configuration_model(aseq, bseq, create_using=None, seed=None):
    """Return a random bipartite graph from two given degree sequences.

    Parameters
    ----------
    aseq : list or iterator
       Degree sequence for node set A.
    bseq : list or iterator
       Degree sequence for node set B.
    create_using : NetworkX graph instance, optional
       Return graph of this type.
    seed : integer, optional
       Seed for random number generator. 

    Nodes from the set A are connected to nodes in the set B by
    choosing randomly from the possible free stubs, one in A and
    one in B.

    Notes
    -----
    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    If no graph type is specified use MultiGraph with parallel edges.
    If you want a graph with no parallel edges use create_using=Graph()
    but then the resulting degree sequences might not be exact.

    The nodes are assigned the attribute 'bipartite' with the value 0 or 1
    to indicate which bipartite set the node belongs to.
    """
    if create_using is None:
        create_using=networkx.MultiGraph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")
        

    G=networkx.empty_graph(0,create_using)

    if not seed is None:
        random.seed(seed)    

    # length and sum of each sequence
    lena=len(aseq)
    lenb=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise networkx.NetworkXError(\
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb))

    G=_add_nodes_with_bipartite_label(G,lena,lenb)
                       
    if max(aseq)==0: return G  # done if no edges

    # build lists of degree-repeated vertex numbers
    stubs=[]
    stubs.extend([[v]*aseq[v] for v in range(0,lena)])  
    astubs=[]
    astubs=[x for subseq in stubs for x in subseq]

    stubs=[]
    stubs.extend([[v]*bseq[v-lena] for v in range(lena,lena+lenb)])  
    bstubs=[]
    bstubs=[x for subseq in stubs for x in subseq]

    # shuffle lists
    random.shuffle(astubs)
    random.shuffle(bstubs)

    G.add_edges_from([[astubs[i],bstubs[i]] for i in range(suma)])

    G.name="bipartite_configuration_model"
    return G


def bipartite_havel_hakimi_graph(aseq, bseq, create_using=None):
    """Return a bipartite graph from two given degree sequences using a 
    Havel-Hakimi style construction.

    Nodes from the set A are connected to nodes in the set B by
    connecting the highest degree nodes in set A to the highest degree
    nodes in set B until all stubs are connected.

    Parameters
    ----------
    aseq : list or iterator
       Degree sequence for node set A.
    bseq : list or iterator
       Degree sequence for node set B.
    create_using : NetworkX graph instance, optional
       Return graph of this type.

    Notes
    -----
    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    If no graph type is specified use MultiGraph with parallel edges.
    If you want a graph with no parallel edges use create_using=Graph()
    but then the resulting degree sequences might not be exact.

    The nodes are assigned the attribute 'bipartite' with the value 0 or 1
    to indicate which bipartite set the node belongs to.
    """
    if create_using is None:
        create_using=networkx.MultiGraph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")

    G=networkx.empty_graph(0,create_using)

    # length of the each sequence
    naseq=len(aseq)
    nbseq=len(bseq)

    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise networkx.NetworkXError(\
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb))

    G=_add_nodes_with_bipartite_label(G,naseq,nbseq)

    if max(aseq)==0: return G  # done if no edges

    # build list of degree-repeated vertex numbers
    astubs=[[aseq[v],v] for v in range(0,naseq)]  
    bstubs=[[bseq[v-naseq],v] for v in range(naseq,naseq+nbseq)]  
    astubs.sort()
    while astubs:
        (degree,u)=astubs.pop() # take of largest degree node in the a set
        if degree==0: break # done, all are zero
        # connect the source to largest degree nodes in the b set
        bstubs.sort()
        for target in bstubs[-degree:]:
            v=target[1]
            G.add_edge(u,v)
            target[0] -= 1  # note this updates bstubs too.
            if target[0]==0:
                bstubs.remove(target)

    G.name="bipartite_havel_hakimi_graph"
    return G

def bipartite_reverse_havel_hakimi_graph(aseq, bseq, create_using=None):
    """Return a bipartite graph from two given degree sequences using a
    Havel-Hakimi style construction.

    Nodes from set A are connected to nodes in the set B by connecting
    the highest degree nodes in set A to the lowest degree nodes in
    set B until all stubs are connected.

    Parameters
    ----------
    aseq : list or iterator
       Degree sequence for node set A.
    bseq : list or iterator
       Degree sequence for node set B.
    create_using : NetworkX graph instance, optional
       Return graph of this type.


    Notes
    -----
    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    If no graph type is specified use MultiGraph with parallel edges.
    If you want a graph with no parallel edges use create_using=Graph()
    but then the resulting degree sequences might not be exact.

    The nodes are assigned the attribute 'bipartite' with the value 0 or 1
    to indicate which bipartite set the node belongs to.
    """
    if create_using is None:
        create_using=networkx.MultiGraph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")

    G=networkx.empty_graph(0,create_using)


    # length of the each sequence
    lena=len(aseq)
    lenb=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise networkx.NetworkXError(\
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb))

    G=_add_nodes_with_bipartite_label(G,lena,lenb)

    if max(aseq)==0: return G  # done if no edges

    # build list of degree-repeated vertex numbers
    astubs=[[aseq[v],v] for v in range(0,lena)]  
    bstubs=[[bseq[v-lena],v] for v in range(lena,lena+lenb)]  
    astubs.sort()
    bstubs.sort()
    while astubs:
        (degree,u)=astubs.pop() # take of largest degree node in the a set
        if degree==0: break # done, all are zero
        # connect the source to the smallest degree nodes in the b set
        for target in bstubs[0:degree]:
            v=target[1]
            G.add_edge(u,v)
            target[0] -= 1  # note this updates bstubs too.
            if target[0]==0:
                bstubs.remove(target)

    G.name="bipartite_reverse_havel_hakimi_graph"
    return G


def bipartite_alternating_havel_hakimi_graph(aseq, bseq,create_using=None):
    """Return a bipartite graph from two given degree sequences using 
    an alternating Havel-Hakimi style construction.

    Nodes from the set A are connected to nodes in the set B by
    connecting the highest degree nodes in set A to alternatively the
    highest and the lowest degree nodes in set B until all stubs are
    connected.

    Parameters
    ----------
    aseq : list or iterator
       Degree sequence for node set A.
    bseq : list or iterator
       Degree sequence for node set B.
    create_using : NetworkX graph instance, optional
       Return graph of this type.


    Notes
    -----
    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    If no graph type is specified use MultiGraph with parallel edges.
    If you want a graph with no parallel edges use create_using=Graph()
    but then the resulting degree sequences might not be exact.

    The nodes are assigned the attribute 'bipartite' with the value 0 or 1
    to indicate which bipartite set the node belongs to.
    """
    if create_using is None:
        create_using=networkx.MultiGraph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")

    G=networkx.empty_graph(0,create_using)

    # length of the each sequence
    naseq=len(aseq)
    nbseq=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise networkx.NetworkXError(\
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb))

    G=_add_nodes_with_bipartite_label(G,naseq,nbseq)

    if max(aseq)==0: return G  # done if no edges
    # build list of degree-repeated vertex numbers
    astubs=[[aseq[v],v] for v in range(0,naseq)]  
    bstubs=[[bseq[v-naseq],v] for v in range(naseq,naseq+nbseq)]  
    while astubs:
        astubs.sort()
        (degree,u)=astubs.pop() # take of largest degree node in the a set
        if degree==0: break # done, all are zero
        bstubs.sort()
        small=bstubs[0:degree // 2]  # add these low degree targets     
        large=bstubs[(-degree+degree // 2):] # and these high degree targets
        stubs=[x for z in zip(large,small) for x in z] # combine, sorry
        if len(stubs)<len(small)+len(large): # check for zip truncation
            stubs.append(large.pop())
        for target in stubs:
            v=target[1]
            G.add_edge(u,v)
            target[0] -= 1  # note this updates bstubs too.
            if target[0]==0:
                bstubs.remove(target)

    G.name="bipartite_alternating_havel_hakimi_graph"
    return G

def bipartite_preferential_attachment_graph(aseq,p,create_using=None,seed=None):
    """Create a bipartite graph with a preferential attachment model from 
    a given single degree sequence.

    Parameters
    ----------
    aseq : list or iterator
       Degree sequence for node set A.
    p :  float
       Probability that a new bottom node is added.
    create_using : NetworkX graph instance, optional
       Return graph of this type.
    seed : integer, optional
       Seed for random number generator. 

    References
    ----------
    .. [1] Jean-Loup Guillaume and Matthieu Latapy,
       Bipartite structure of all complex networks,
       Inf. Process. Lett. 90, 2004, pg. 215-221
       http://dx.doi.org/10.1016/j.ipl.2004.03.007
    """
    if create_using is None:
        create_using=networkx.MultiGraph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")

    if p > 1: 
        raise networkx.NetworkXError("probability %s > 1"%(p))

    G=networkx.empty_graph(0,create_using)

    if not seed is None:
        random.seed(seed)    

    naseq=len(aseq)
    G=_add_nodes_with_bipartite_label(G,naseq,0)
    vv=[ [v]*aseq[v] for v in range(0,naseq)]
    while vv:
        while vv[0]:
            source=vv[0][0]
            vv[0].remove(source)
            if random.random() < p or G.number_of_nodes() == naseq:
                target=G.number_of_nodes()
                G.add_node(target,bipartite=1)
                G.add_edge(source,target)
            else:
                bb=[ [b]*G.degree(b) for b in range(naseq,G.number_of_nodes())]
                # flatten the list of lists into a list.
                bbstubs=reduce(lambda x,y: x+y, bb) 
                # choose preferentially a bottom node.
                target=random.choice(bbstubs) 
                G.add_node(target,bipartite=1)
                G.add_edge(source,target)
        vv.remove(vv[0])
    G.name="bipartite_preferential_attachment_model"
    return G


def bipartite_random_regular_graph(d, n, create_using=None,seed=None):
    """Experimental: Generate a random regular bipartite graph.

    Parameters
    ----------
    d : integer
      Degree of graph.
    n : integer
      Number of nodes in graph.
    create_using : NetworkX graph instance, optional
      Return graph of this type.
    seed : integer, optional
       Seed for random number generator. 

    Notes
    ------
    This is an untested, unproved algorithm.

    Nodes are numbered 0...n-1. 

    Restrictions on n and d:
       -  n must be even
       -  n>=2*d

    Algorithm inspired by random_regular_graph()
    """
    # This algorithm could be improved - see random_regular_graph()
    # helper subroutine to check for suitable edges
    def suitable(leftstubs,rightstubs):
        for s in leftstubs:
            for t in rightstubs:
                if not t in seen_edges[s]:
                    return True
        # else no suitable possible edges
        return False  

    if not n*d%2==0:
        print("n*d must be even")
        return False


    if not n%2==0:
        print("n must be even")
        return False

    if not n>=2*d:
        print("n must be >= 2*d")
        return False


    if create_using is None:
        create_using=networkx.Graph()
    elif create_using.is_directed():
        raise networkx.NetworkXError(\
                "Directed Graph not supported")

    if not seed is None:
        random.seed(seed)    

    G=networkx.empty_graph(0,create_using)
    G=_add_nodes_with_bipartite_label(G,n/2,n/2)
    nodes=range(0,n)
    seen_edges={} 
    [seen_edges.setdefault(v,{}) for v in nodes]

    vv=[ [v]*d for v in nodes ]   # List of degree-repeated vertex numbers
    stubs=reduce(lambda x,y: x+y ,vv)  # flatten the list of lists to a list

    leftstubs=stubs[:(n*d // 2)]
    rightstubs=stubs[n*d // 2:]

    while leftstubs:
       source=random.choice(leftstubs)
       target=random.choice(rightstubs)
       if source!=target and not target in seen_edges[source]:
           leftstubs.remove(source)
           rightstubs.remove(target)
           seen_edges[source][target]=1
           seen_edges[target][source]=1
           G.add_edge(source,target)
       else:
           # further check to see if suitable 
           if suitable(leftstubs,rightstubs)==False: 
               return False
    return G


def bipartite_random_graph(n, m, p, seed=None, directed=False):
    """Return a bipartite random graph.

    This is a bipartite version of the binomial (Erdős-Rényi) graph.

    Parameters
    ----------
    n : int
        The number of nodes in the first bipartite set.
    m : int
        The number of nodes in the second bipartite set.
    p : float
        Probability for edge creation.
    seed : int, optional
        Seed for random number generator (default=None). 
    directed : bool, optional (default=False)
        If True return a directed graph 
      
    Notes
    -----
    The bipartite random graph algorithm chooses each of the n*m (undirected) 
    or 2*nm (directed) possible edges with probability p.

    This algorithm is O(n+m) where m is the expected number of edges.
    
    The nodes are assigned the attribute 'bipartite' with the value 0 or 1
    to indicate which bipartite set the node belongs to.

    See Also
    --------
    gnp_random_graph, bipartite_configuration_model

    References
    ----------
    .. [1] Vladimir Batagelj and Ulrik Brandes, 
       "Efficient generation of large random networks",
       Phys. Rev. E, 71, 036113, 2005.
    """
    G=nx.Graph()
    G=_add_nodes_with_bipartite_label(G,n,m)
    if directed:
        G=nx.DiGraph(G)
    G.name="fast_gnp_random_graph(%s,%s,%s)"%(n,m,p)

    if not seed is None:
        random.seed(seed)

    if p <= 0:
        return G
    if p >= 1:
        return nx.complete_bipartite_graph(n,m)
        
    lp = math.log(1.0 - p)  

    v = 0 
    w = -1
    while v < n:
        lr = math.log(1.0 - random.random())
        w = w + 1 + int(lr/lp)
        while w >= m and v < n:
            w = w - m
            v = v + 1
        if v < n:
            G.add_edge(v, n+w)

    if directed:
        # use the same algorithm to 
        # add edges from the "m" to "n" set
        v = 0 
        w = -1
        while v < n:
            lr = math.log(1.0 - random.random())
            w = w + 1 + int(lr/lp)
            while  w>= m and v < n:
                w = w - m
                v = v + 1
            if v < n:
                G.add_edge(n+w, v)

    return G


def _add_nodes_with_bipartite_label(G, lena, lenb):
    G.add_nodes_from(range(0,lena+lenb))
    b=dict(zip(range(0,lena),[0]*lena))
    b.update(dict(zip(range(lena,lena+lenb),[1]*lenb)))
    nx.set_node_attributes(G,'bipartite',b)
    return G
