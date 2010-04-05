#!/usr/bin/env python
"""
Sampson's monastery data.

Shows how to read data from a zip file and plot multiple frames. 

"""
__author__ = """Aric Hagberg (hagberg@lanl.gov)"""
#    Copyright (C) 2010 by 
#    Aric Hagberg <hagberg@lanl.gov>
#    Dan Schult <dschult@colgate.edu>
#    Pieter Swart <swart@lanl.gov>
#    All rights reserved.
#    BSD license.

import zipfile, cStringIO
import networkx as nx
import matplotlib.pyplot as plt

zf = zipfile.ZipFile('sampson_data.zip') # zipfile object
e1=cStringIO.StringIO(zf.read('samplike1.txt')) # read info file
e2=cStringIO.StringIO(zf.read('samplike2.txt')) # read info file
e3=cStringIO.StringIO(zf.read('samplike3.txt')) # read info file
G1=nx.read_edgelist(e1,delimiter='\t')
G2=nx.read_edgelist(e2,delimiter='\t')
G3=nx.read_edgelist(e3,delimiter='\t')
pos=nx.spring_layout(G3,iterations=100)
plt.clf()

plt.subplot(221)
plt.title('samplike1')
nx.draw(G1,pos,node_size=50,with_labels=False)
plt.subplot(222)
plt.title('samplike2')
nx.draw(G2,pos,node_size=50,with_labels=False)
plt.subplot(223)
plt.title('samplike3')
nx.draw(G3,pos,node_size=50,with_labels=False)
plt.subplot(224)
plt.title('samplike1,2,3')
nx.draw(G3,pos,edgelist=G3.edges(),node_size=50,with_labels=False)
nx.draw_networkx_edges(G1,pos,alpha=0.25)
nx.draw_networkx_edges(G2,pos,alpha=0.25)
plt.savefig("sampson.png") # save as png
plt.show() # display

