#!/usr/bin/env python
"""
Atlas of all graphs of 6 nodes or less.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-05-19 14:23:02 -0600 (Thu, 19 May 2005) $"
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from NX import *
from NX.generators.atlas import *
from NX.isomorph import graph_could_be_isomorphic as isomorphic
import random

def atlas6():
    """ Return the atlas of all connected graphs of 6 nodes or less.
        Attempt to check for isomorphisms and remove.
    """

    Atlas=graph_atlas_g()[0:208] # 208
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

    from NX import *

    G=atlas6()

    print "graph has %d nodes with %d edges"\
          %(number_of_nodes(G),number_of_edges(G))
    print number_connected_components(G),"connected components"

    # layout graphs with positions using graphviz neato
    pos=pydot_layout(G,prog="neato")

    # color nodes
    C=connected_component_subgraphs(G)
    c={}
    for g in C:
#        o=g.order()
        o=random.random() # random color...
        for n in g:
            c[n]=o
            
    figure(1,figsize=(10,10))
    draw_nx(G,pos,node_size=40,node_labels=False,node_color=c)


