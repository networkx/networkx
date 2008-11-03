# -*- coding: utf-8 -*-
"""
Generators and functions for bipartite graphs.

"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nPieter Swart (swart@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
 
__all__=[]

import random
import sys
import networkx as NX

def bipartite_configuration_model(aseq, bseq,
                                  create_using=None,
                                  seed=None,
                                  ):
    """
    Return a random bipartite graph from two given degree sequences.

    :Parameters:
       - `aseq`: degree sequence for node set A
       - `bseq`: degree sequence for node set B

    Nodes from the set A are connected to nodes in the set B by
    choosing randomly from the possible free stubs, one in A and
    one in B.

    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)

    If no graph type is specified use MultiGraph with parallel edges.

    If you want a graph with no parallel edges use create_using=Graph()
    but then the resulting degree sequences might not be exact.

    """

    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)

    if not seed is None:
        random.seed(seed)    

    # length and sum of each sequence
    lena=len(aseq)
    lenb=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise NX.NetworkXError, \
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb)

    G.add_nodes_from(range(0,lena+lenb))

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

    G.add_edges_from([[astubs[i],bstubs[i]] for i in xrange(suma)])

    G.name="bipartite_configuration_model"
    return G


def bipartite_havel_hakimi_graph(aseq, bseq,
                                 create_using=None,
                                 ):
    """
    Return a bipartite graph from two given degree sequences
    using a Havel-Hakimi style construction.

    :Parameters:
       - `aseq`: degree sequence for node set A
       - `bseq`: degree sequence for node set B

    Nodes from the set A are connected to nodes in the set B by
    connecting the highest degree nodes in set A to
    the highest degree nodes in set B until all stubs are connected.

    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    """
    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)

    # length of the each sequence
    naseq=len(aseq)
    nbseq=len(bseq)

    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise NX.NetworkXError, \
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb)

    G.add_nodes_from(range(0,naseq)) # one vertex type (a)
    G.add_nodes_from(range(naseq,naseq+nbseq)) # the other type (b)

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

def bipartite_reverse_havel_hakimi_graph(aseq, bseq,
                                         create_using=None,
                                         ):
    """
    Return a bipartite graph from two given degree sequences
    using a "reverse" Havel-Hakimi style construction.

    :Parameters:
       - `aseq`: degree sequence for node set A
       - `bseq`: degree sequence for node set B

    Nodes from the set A are connected to nodes in the set B by
    connecting the highest degree nodes in set A to
    the lowest degree nodes in set B until all stubs are connected.

    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    """
    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)


    # length of the each sequence
    lena=len(aseq)
    lenb=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise NX.NetworkXError, \
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb)

    G.add_nodes_from(range(0,lena+lenb))
    

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


def bipartite_alternating_havel_hakimi_graph(aseq, bseq,
                                            create_using=None,
                                            ):
    """
    Return a bipartite graph from two given degree sequences
    using a alternating Havel-Hakimi style construction.

    :Parameters:
       - `aseq`: degree sequence for node set A
       - `bseq`: degree sequence for node set B

    Nodes from the set A are connected to nodes in the set B by
    connecting the highest degree nodes in set A to
    alternatively the highest and the lowest degree nodes in set
    B until all stubs are connected.

    The sum of the two sequences must be equal: sum(aseq)=sum(bseq)
    """
    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)

    # length of the each sequence
    naseq=len(aseq)
    nbseq=len(bseq)
    suma=sum(aseq)
    sumb=sum(bseq)

    if not suma==sumb:
        raise NX.NetworkXError, \
              'invalid degree sequences, sum(aseq)!=sum(bseq),%s,%s'\
              %(suma,sumb)

    G.add_nodes_from(range(0,naseq)) # one vertex type (a)
    G.add_nodes_from(range(naseq,naseq+nbseq)) # the other type (b)

    if max(aseq)==0: return G  # done if no edges
    # build list of degree-repeated vertex numbers
    astubs=[[aseq[v],v] for v in range(0,naseq)]  
    bstubs=[[bseq[v-naseq],v] for v in range(naseq,naseq+nbseq)]  
    while astubs:
        astubs.sort()
        (degree,u)=astubs.pop() # take of largest degree node in the a set
        if degree==0: break # done, all are zero
        bstubs.sort()
        small=bstubs[0:degree/2]  # add these low degree targets     
        large=bstubs[(-degree+degree/2):] # and these high degree targets
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

def bipartite_preferential_attachment_graph(aseq,p,
                                            create_using=None,
                                            ):
    """
    Create a bipartite graph with a preferential attachment model
    from a given single "top" degree sequence.

    :Parameters:
       - `aseq`: degree sequence for node set A (top)
       - `p`:    probability that a new bottom node is added


    Reference::

     @article{guillaume-2004-bipartite,
       author = {Jean-Loup Guillaume and Matthieu Latapy},
       title = {Bipartite structure of all complex networks},
       journal = {Inf. Process. Lett.},
       volume = {90},
       number = {5},
       year = {2004},
       issn = {0020-0190},
       pages = {215--221},
       doi = {http://dx.doi.org/10.1016/j.ipl.2004.03.007},
       publisher = {Elsevier North-Holland, Inc.},
       address = {Amsterdam, The Netherlands, The Netherlands},
       }

    """
    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)

    if p > 1: 
        raise NX.NetworkXError, "probability %s > 1"%(p)

    naseq=len(aseq)
    G.add_nodes_from(range(0,naseq))
    vv=[ [v]*aseq[v] for v in range(0,naseq)]
    while vv:
        while vv[0]:
            source=vv[0][0]
            vv[0].remove(source)
            if random.random() < p or G.number_of_nodes() == naseq:
                target=G.number_of_nodes()
                G.add_edge(source,target)
            else:
                bb=[ [b]*G.degree(b) for b in range(naseq,G.number_of_nodes())]
                # flatten the list of lists into a list.
                bbstubs=reduce(lambda x,y: x+y, bb) 
                # choose preferentially a bottom node.
                target=random.choice(bbstubs) 
                G.add_edge(source,target)
        vv.remove(vv[0])
    G.name="bipartite_preferential_attachment_model"
    return G


def bipartite_random_regular_graph(d, n,
                                   create_using=None,
                                   ):
    """
    UNTESTED:Generate a random bipartite graph of n nodes each with degree d.

    Restrictions on n and d:
       -  n must be even
       -  n>=2*d

    Nodes are numbered 0...n-1. 
    
    Algorithm inspired by random_regular_graph()

    """
    # helper subroutine to check for suitable edges
    def suitable(leftstubs,rightstubs):
        for s in leftstubs:
            for t in rightstubs:
                if not t in seen_edges[s]:
                    return True
        # else no suitable possible edges
        return False  

    if not n*d%2==0:
        print "n*d must be even"
        return False


    if not n%2==0:
        print "n must be even"
        return False

    if not n>=2*d:
        print "n must be >= 2*d"
        return False


    if create_using==None:
        create_using=NX.MultiGraph()

    G=NX.empty_graph(0,create_using)

    nodes=range(0,n)
    G.add_nodes_from(nodes)

    seen_edges={} 
    [seen_edges.setdefault(v,{}) for v in nodes]

    vv=[ [v]*d for v in nodes ]   # List of degree-repeated vertex numbers
    stubs=reduce(lambda x,y: x+y ,vv)  # flatten the list of lists to a list

    leftstubs=stubs[:(n*d/2)]
    rightstubs=stubs[n*d/2:]

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


def project(B,nodes,create_using=None):
    """
    Returns a graph that is the projection of the bipartite graph B
    onto the set of nodes given in list nodes.
    
    The nodes retain their names and are connected if they share a
    common node in the node set of {B not nodes }.
 
    No attempt is made to verify that the input graph B is bipartite.
    """

    if create_using==None:
        create_using=NX.Graph()

    G=NX.empty_graph(0,create_using)

    for v in nodes:
        G.add_node(v)
        for cv in B.neighbors(v):
            G.add_edges_from([(v,u) for u in B.neighbors(cv)])
    return G


def bipartite_color(G):
    color={}
    for n in G.nodes(): #handle disconnected graphs
        if n in color: continue
        queue=[n]  
        color[n]=1 # nodes seen with color (1 or 0)
        while queue:
            v=queue.pop()
            c=1-color[v] # opposite color of node v
            for w in G.neighbors(v): 
                if w in color: 
                    if color[w]==color[v]:
                        raise NX.NetworkXError, "graph is not bipartite"
                else:
                    color[w]=c
                    queue.append(w)
    return color

def is_bipartite(G):
    """ Returns True if graph G is bipartite, False if not.

    Traverse the graph G with depth-first-search and color nodes.
    """
    try:
        bipartite_color(G)
        return True
    except:
        return False
    
def bipartite_sets(G):
    """
    Returns (X,Y) where X and Y are the nodes in each bipartite set
    of graph G.  Fails with an error if graph is not bipartite.
    """
    color=bipartite_color(G)
    X=[n for n in color if color[n]==1]
    Y=[n for n in color if color[n]==0]
    return (X,Y)

