#!/usr/bin/env python
"""
Routes to LANL from 186 sites on the Internet.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
__date__ = "$Date: 2005-04-01 11:51:23 -0700 (Fri, 01 Apr 2005) $"
__credits__ = """"""
__revision__ = ""
#    Copyright (C) 2004 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *
import re
import sys

def lanl_graph():
    """ Return the lanl internet view graph from lanl.edges
    """
    try:
        fh=open("lanl.edges","r")
    except IOError:
        print "lanl.edges not found"
        raise

    G=Graph()

    time={}
    time[0]=0 # assign 0 to center node
    for line in fh.readlines():
        (head,tail,rtt)=line.split()
        G.add_edge(int(head),int(tail))
        time[int(head)]=float(rtt)

    # get largest component and assign ping times to G0time dictionary        
    G0=connected_component_subgraphs(G)[0]   
    G0.rtt={}
    for n in G0:
        G0.rtt[n]=time[n]

    return G0

if __name__ == '__main__':

    from networkx import *

    G=lanl_graph()


    print "graph has %d nodes with %d edges"\
          %(number_of_nodes(G),number_of_edges(G))
    print number_connected_components(G),"connected components"

    # draw in radial layout with graphviz
    #pos=pydot_layout(G,prog="twopi",root=0)
    # draw_nx(G,pos,node_labels=False,node_size=10)
    # colored by rtt ping time
    #draw_nx(G,pos,node_color=G.rtt,node_labels=False,node_size=10)
