#!/usr/bin/env python
"""
Random graph from given degree sequence.
Draw degree histogram with matplotlib.

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""

try:
    import matplotlib.pyplot as plt
    import matplotlib
except:
    raise

import networkx as nx

z=nx.utils.create_degree_sequence(100,nx.utils.powerlaw_sequence,exponent=2.1)
nx.is_valid_degree_sequence(z)

print "Configuration model"
G=nx.configuration_model(z)  # configuration model

degree_sequence=sorted(nx.degree(G).values(),reverse=True) # degree sequence
#print "Degree sequence", degree_sequence
dmax=max(degree_sequence)

plt.loglog(degree_sequence,'b-',marker='o')
plt.title("Degree rank plot")
plt.ylabel("degree")
plt.xlabel("rank")

# draw graph in inset 
plt.axes([0.45,0.45,0.45,0.45])
Gcc=nx.connected_component_subgraphs(G)[0]
pos=nx.spring_layout(Gcc)
plt.axis('off')
nx.draw_networkx_nodes(Gcc,pos,node_size=20)
nx.draw_networkx_edges(Gcc,pos,alpha=0.4)

plt.savefig("degree_histogram.png")
plt.show()

