# -*- coding: utf-8 -*-
"""smax graph
"""
#    Copyright (C) 2004-2011 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.
import heapq
import networkx as nx
from networkx.generators.classic import empty_graph

__author__ = "\n".join(['Aric Hagberg (hagberg@lanl.gov)',
                        'Pieter Swart (swart@lanl.gov)',
                        'Dan Schult (dschult@colgate.edu)'])

__all__ = ['li_smax_graph']


def li_smax_graph(degree_seq, create_using=None):
    """Generates a graph based with a given degree sequence and maximizing
    the s-metric.  Experimental implementation.

    Maximum s-metrix  means that high degree nodes are connected to high
    degree nodes. 
        
    - `degree_seq`: degree sequence, a list of integers with each entry
       corresponding to the degree of a node.
       A non-graphical degree sequence raises an Exception.    

    Reference::      
    
      @unpublished{li-2005,
       author = {Lun Li and David Alderson and Reiko Tanaka
                and John C. Doyle and Walter Willinger},
       title = {Towards a Theory of Scale-Free Graphs:
               Definition, Properties, and  Implications (Extended Version)},
       url = {http://arxiv.org/abs/cond-mat/0501169},
       year = {2005}
      }

    The algorithm::

     STEP 0 - Initialization
     A = {0}
     B = {1, 2, 3, ..., n}
     O = {(i; j), ..., (k, l),...} where i < j, i <= k < l and 
             d_i * d_j >= d_k *d_l 
     wA = d_1
     dB = sum(degrees)

     STEP 1 - Link selection
     (a) If |O| = 0 TERMINATE. Return graph A.
     (b) Select element(s) (i, j) in O having the largest d_i * d_j , if for 
             any i or j either w_i = 0 or w_j = 0 delete (i, j) from O
     (c) If there are no elements selected go to (a).
     (d) Select the link (i, j) having the largest value w_i (where for each 
             (i, j) w_i is the smaller of w_i and w_j ), and proceed to STEP 2.

     STEP 2 - Link addition
     Type 1: i in A and j in B. 
             Add j to the graph A and remove it from the set B add a link 
             (i, j) to the graph A. Update variables:
             wA = wA + d_j -2 and dB = dB - d_j
             Decrement w_i and w_j with one. Delete (i, j) from O
     Type 2: i and j in A.
         Check Tree Condition: If dB = 2 * |B| - wA. 
             Delete (i, j) from O, continue to STEP 3
         Check Disconnected Cluster Condition: If wA = 2. 
             Delete (i, j) from O, continue to STEP 3
         Add the link (i, j) to the graph A 
         Decrement w_i and w_j with one, and wA = wA -2
     STEP 3
         Go to STEP 1


    The article states that the algorithm will result in a maximal s-metric. 
    This implementation can not guarantee such maximality. I may have 
    misunderstood the algorithm, but I can not see how it can be anything 
    but a heuristic. Please contact me at sundsdal@gmail.com if you can 
    provide python code that can guarantee maximality.
    Several optimizations are included in this code and it may be hard to read.
    Commented code to come.

    A POSSIBLE ALTERNATIVE:

    For an 'unconstrained' graph, that is one they describe as having
    the sum of the degree sequence be even(ie all undirected graphs) they
    present a simpler algorithm. It is as follows

        "For each vertex i: if di is even then attach di/2 self-loops;
        if di is odd, then attach (di-1)/2 self-loops, leaving one
        available "stub". Second for all remaining vertices with "stubs"
        connect them in pairs according to decreasing values of di."[1]
    
    Since this only works for undirected graphs anyway, perhaps this is
    the better method? Note this also returns a graph with a larger
    s_metric than the other method, and it seems to have the same
    degree sequence, though I haven't tested it extensively.
    """
    if not nx.is_valid_degree_sequence(degree_seq):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")

    degree_seq.sort(reverse=True) # make sure it's sorted
   
    if not (sum(degree_seq) %2): #check if the sum of the degree sequence is even, Should be if it is undirected
        dseven = [di for di in degree_seq if (not di % 2)]
        dsodd = [di for di in degree_seq if (di % 2)]
        Gmax = nx.MultiGraph()
        i = 0
        for di in dseven:
            Gmax.add_node(i)
            for k in range(di // 2):
                Gmax.add_edge(i,i)
            i=i+1
        for j in range(0,len(dsodd),2): #do this iteratively to connect
            Gmax.add_node(i)            #node stubs as we go
            Gmax.add_node(i+1)
            for k in range((dsodd[j]-1) // 2):
                Gmax.add_edge(i,i)
            for k in range((dsodd[j+1]-1) // 2):
                Gmax.add_edge(i+1,i+1)
            Gmax.add_edge(i,i+1)
            i=i+2
        return Gmax
    else:
        degrees_left = degree_seq[:]
        A_graph = empty_graph(0,create_using)
        A_graph.add_node(0)
        a_list = [False]*len(degree_seq)
        b_set = set(range(1,len(degree_seq)))
        a_open = set([0])
        O = []
        for j in b_set:
            heapq.heappush(O, (-degree_seq[0]*degree_seq[j], (0,j))),
        wa = degrees_left[0] #stubs in a_graph
        db = sum(degree_seq) - degree_seq[0] #stubs in b-graph
        a_list[0] = True #node 0 is now in a_Graph
        bsize = len(degree_seq) -1 #size of b_graph
        selected = []
        weight = 0
        while O or selected:
            if len(selected) <1 :
                firstrun = True
                while O:
                    (newweight, (i,j)) = heapq.heappop(O)
                    if degrees_left[i] < 1 or degrees_left[j] < 1 :
                        continue
                    if firstrun:
                        firstrun = False
                        weight = newweight
                    if not newweight == weight:
                        break
                    heapq.heappush(selected, [-degrees_left[i], \
                                        -degrees_left[j], (i,j)])
                if not weight == newweight:
                    heapq.heappush(O,(newweight, (i,j)))
                weight *= -1
            if len(selected) < 1:
                break

            [w1, w2, (i,j)] = heapq.heappop(selected)
            if degrees_left[i] < 1 or degrees_left[j] < 1 :
                continue
            if a_list[i] and j in b_set:
                #TYPE1
                a_list[j] = True
                b_set.remove(j)
                A_graph.add_node(j)
                A_graph.add_edge(i, j)
                degrees_left[i] -= 1
                degrees_left[j] -= 1
                wa += degree_seq[j] - 2
                db -= degree_seq[j]
                bsize -= 1
                newweight = weight
                if not degrees_left[j] == 0:
                    a_open.add(j)
                    for k in b_set:
                        if A_graph.has_edge(j, k): continue
                        w = degree_seq[j]*degree_seq[k]
                        if w > newweight:
                            newweight = w
                        if weight == w and not newweight > weight:
                            heapq.heappush(selected, [-degrees_left[j], \
                                                -degrees_left[k], (j,k)])
                        else:
                            heapq.heappush(O, (-w, (j,k)))
                    if not weight == newweight:
                        while selected:
                            [w1,w2,(i,j)] = heapq.heappop(selected)
                            if degrees_left[i]*degrees_left[j] > 0:
                                heapq.heappush(O, [-degree_seq[i]*degree_seq[j],(i,j)])
                if degrees_left[i] == 0:
                    a_open.discard(i)

            else:
                #TYPE2
                if db == (2*bsize - wa):
                    #tree condition
                    #print "removing because tree condition    "
                    continue
                elif db < 2*bsize -wa:
                    raise nx.NetworkXError(\
                            "THIS SHOULD NOT HAPPEN!-not graphable")
                    continue
                elif wa == 2 and bsize > 0:
                    #print "removing because disconnected  cluster"
                    #disconnected cluster condition
                    continue
                elif wa == db - (bsize)*(bsize-1):
                    #print "MYOWN removing because disconnected  cluster"
                    continue
                A_graph.add_edge(i, j)
                degrees_left[i] -= 1
                degrees_left[j] -= 1
                if degrees_left[i] < 1:
                    a_open.discard(i)
                if degrees_left[j] < 1:
                    a_open.discard(j)
                wa -=  2
                if not degrees_left[i] < 0 and not degrees_left[j] < 0:
                    selected2 = (selected)
                    selected = []
                    while selected2:
                        [w1,w1, (i,j)] = heapq.heappop(selected2)
                        if degrees_left[i]*degrees_left[j] > 0:
                            heapq.heappush(selected, [-degrees_left[i], \
                                            -degrees_left[j], (i,j)])
        return A_graph 

def connected_smax_graph(degree_seq, create_using=None):
    """
    Not implemented.
    """
    # incomplete implementation
    
    if not is_valid_degree_sequence(degree_seq):
        raise nx.NetworkXError('Invalid degree sequence')
    if create_using is not None and create_using.is_directed():
        raise nx.NetworkXError("Directed Graph not supported")
   
    # build dictionary of node id and degree, sorted by degree, largest first
    degree_seq.sort() 
    degree_seq.reverse()
    ddict=dict(zip(range(len(degree_seq)),degree_seq))

    G=empty_graph(1,create_using) # start with single node

    return False

