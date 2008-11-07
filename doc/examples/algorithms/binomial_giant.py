#!/usr/bin/env python
"""
This example illustrates the sudden appearance of a 
giant connected component in a binomial random graph.

Requires graphviz and pylab to draw.

"""
#    Copyright (C) 2006 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

from networkx import *
try:
    import pylab as P
except:
    print "pylab not found: see https://networkx.lanl.gov/Drawing.html for info"
    raise 

from math import *

n=150  # 150 nodes
p_giant=1.0/(n-1)      # p value at which giant component 
                       # (of size log(n) nodes) is expected
p_conn=log(n)/float(n) # p value at which graph is expected
                       # to become completely connected
# the next range of p values should be close to the above threshold
pvals=[0.003, 0.006, 0.008, 0.015] 

region=220 # for pylab 2x2 subplot layout
try: # drawing
     for p in pvals:    
	 G=binomial_graph(n,p)
	 pos=graphviz_layout(G)
	 region+=1
	 P.subplot(region)
         P.title("p = %6.3f"%(p))
	 draw(G,pos,
	      with_labels=False,
	      node_size=10
              )
         # identify largest connected component
         Gcc=connected_component_subgraphs(G)
         G0=Gcc[0] 
         draw_networkx_edges(G0,pos,
                             with_labels=False,
                             edge_color='r',
                             width=6.0
                             )
         # show other connected components
         for Gi in Gcc[1:]:
            if len(Gi)>1:
               draw_networkx_edges(Gi,pos,
                                   with_labels=False,
                                   edge_color='r',
                                   alpha=0.3,
                                   width=5.0
                                   )         
     P.savefig("binomial_giant.png")
     P.show() # display
except:
	print "Unable to draw: cannot find graphviz or pylab"

 