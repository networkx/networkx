#!/usr/bin/env python
"""
Atlas of all graphs of 6 nodes or less.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2008 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *
from networkx.generators.atlas import *
from networkx import graph_could_be_isomorphic as isomorphic
import random

def atlas6():
    """ Return the atlas of all connected graphs of 6 nodes or less.
        Attempt to check for isomorphisms and remove.
    """

    Atlas=graph_atlas_g()[0:158] # 208
    # remove isolated nodes, only connected graphs are left
    U=Graph() # graph for union of all graphs in atlas
    for G in Atlas: 
        zerodegree=[n for n in G if G.degree(n)==0]
        for n in zerodegree:
            G.delete_node(n)
        U=disjoint_union(U,G)

    # list of graphs of all connected components        
    C=connected_component_subgraphs(U)        
    
    UU=Graph()        
    # do quick isomorphic-like check, not a true isomorphism checker     
    nlist=[] # list of nonisomorphic graphs
    for G in C:
        # check against all nonisomorphic graphs so far
        if not iso(G,nlist):
            nlist.append(G)
            UU=disjoint_union(UU,G) # union the nonisomorphic graphs  
    return UU            

def iso(G1, glist):
    """Quick and dirty nonisomorphism checker used to check isomorphisms."""
    for G2 in glist:
        if isomorphic(G1,G2):
            return True
    return False        


if __name__ == '__main__':

    import networkx as nx
    
    import random

    G=atlas6()

    print "graph has %d nodes with %d edges"\
          %(number_of_nodes(G),number_of_edges(G))
    print number_connected_components(G),"connected components"
    C=nx.connected_component_subgraphs(G)
    UG=nx.UbiGraph(G)
    for g in C:
        x = random.randint(0,256*256*256)
        UG.set_node_attr(g.nodes(),color='#%06x'%x)
