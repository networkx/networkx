#!/usr/bin/env python
"""
Draw a graph with matplotlib.
You must have matplotlib for this to work.
"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2004-2008
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    Distributed under the terms of the GNU Lesser General Public License
#    http://www.gnu.org/copyleft/lesser.html

try:
    import matplotlib.pyplot as plt
except:
    raise

import networkx as nx

G=nx.grid_2d_graph(4,4)  #4x4 grid

pos=nx.spring_layout(G)

plt.subplot(221)
nx.draw(G,pos) 

plt.subplot(222)
nx.draw(G,pos,node_color='k',node_size=20,with_labels=False) 

plt.subplot(223)
nx.draw(G,pos,node_color='g',node_size=20,with_labels=False) 

plt.subplot(224)
H=G.to_directed()
nx.draw(H,pos,node_color='b',node_size=20,with_labels=False) 

plt.show()
