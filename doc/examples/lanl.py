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

    try: # drawing
        import pylab as P

	# specify pylab plot layout & background 
	ax=P.subplot(111,axisbg='lightgrey')
	# turn off x and y axes labels in pylab
	P.xticks([])
	P.yticks([])

        # use graphviz to find radial layout
        pos=graphviz_layout(G,prog="twopi",root=0)
        # draw nodes, coloring by rtt ping time
        draw_networkx_nodes(G,pos,
             node_color=P.array([G.rtt[v] for v in G]),
             with_labels=False,
             alpha=0.4,
             node_size=20)
        draw_networkx_edges(G,pos,alpha=0.4)
        P.savefig("lanl.png")
        print "Wrote lanl.png"
    except:
        print "This example could not find pylab or graphviz for drawing."
        pass
