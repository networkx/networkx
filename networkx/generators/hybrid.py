"""
Hybrid 

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)\nDan Schult (dschult@colgate.edu)"""
#    Copyright (C) 2004-2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

_all__ = ['kl_connected_subgraph', 'is_kl_connected']

import copy
import networkx as nx

def kl_connected_subgraph(G,k,l,low_memory=False,same_as_graph=False):
    """ Returns the maximum locally (k,l) connected subgraph of G.

        (k,l)-connected subgraphs are presented by Fan Chung and Li
        in "The Small World Phenomenon in hybrid power law graphs"
        to appear in "Complex Networks" (Ed. E. Ben-Naim) Lecture
        Notes in Physics, Springer (2004)

        low_memory=True then use a slightly slower, but  lower memory version
        same_as_graph=True then return a tuple with subgraph and
        pflag for if G is kl-connected
    """
    H=copy.deepcopy(G)    # subgraph we construct by removing from G
    
    graphOK=True
    deleted_some=True # hack to start off the while loop
    while deleted_some:
        deleted_some=False
        for edge in H.edges():
            (u,v)=edge
            ### Get copy of graph needed for this search
            if low_memory:
                verts=set([u,v])
                for i in range(k):
                    [verts.update(G.neighbors(w)) for w in verts.copy()]
                G2=G.subgraph(list(verts))
            else:
                G2=copy.deepcopy(G)
            ###
            path=[u,v]
            cnt=0
            accept=0
            while path:
                cnt += 1 # Found a path
                if cnt>=l:
                    accept=1
                    break
                # record edges along this graph
                prev=u
                for w in path:
                    if prev!=w:
                        G2.remove_edge(prev,w)
                        prev=w
#                path=shortest_path(G2,u,v,k) # ??? should "Cutoff" be k+1?
                try:
                    path=nx.shortest_path(G2,u,v) # ??? should "Cutoff" be k+1?
                except nx.NetworkXNoPath:
                    path = False
            # No Other Paths
            if accept==0:
                H.remove_edge(u,v)
                deleted_some=True
                if graphOK: graphOK=False
    # We looked through all edges and removed none of them.
    # So, H is the maximal (k,l)-connected subgraph of G
    if same_as_graph:
        return (H,graphOK)
    return H

def is_kl_connected(G,k,l,low_memory=False):
    """Returns True if G is kl connected."""
    graphOK=True
    for edge in G.edges():
        (u,v)=edge
        ### Get copy of graph needed for this search
        if low_memory:
            verts=set([u,v])
            for i in range(k):
                [verts.update(G.neighbors(w)) for w in verts.copy()]
            G2=G.subgraph(verts)
        else:
            G2=copy.deepcopy(G)
        ###
        path=[u,v]
        cnt=0
        accept=0
        while path:
            cnt += 1 # Found a path
            if cnt>=l:
                accept=1
                break
            # record edges along this graph
            prev=u
            for w in path:
                if w!=prev:
                    G2.remove_edge(prev,w)
                    prev=w
#            path=shortest_path(G2,u,v,k) # ??? should "Cutoff" be k+1?
            try:
                path=nx.shortest_path(G2,u,v) # ??? should "Cutoff" be k+1?
            except nx.NetworkXNoPath:
                path = False
        # No Other Paths
        if accept==0:
            graphOK=False
            break
    # return status
    return graphOK

