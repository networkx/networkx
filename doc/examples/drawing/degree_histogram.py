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

z=nx.create_degree_sequence(1000,nx.utils.powerlaw_sequence)
nx.is_valid_degree_sequence(z)

print "Configuration model"
G=nx.configuration_model(z)  # configuration model

degree_sequence=nx.degree(G) # degree sequence
print "Degree sequence", degree_sequence
dmax=max(degree_sequence)
print "Degree histogram, max degree:",dmax
#h,bins=mlab.hist(degree_sequence,bins=dmax)
h,bins=matplotlib.numpy.histogram(degree_sequence,bins=dmax,new=True)

# draw x-y plot
hmax=max(h)
plt.axis([1,dmax,1,hmax]) # set ranges
#x=compress(h,bins)    # remove bins with zero entries
#y=compress(h,h)       # remove corresponding entries
x=bins.compress(h)
y=h.compress(h)
plt.loglog(x,y,'bo')
plt.title("Degree distribution")
plt.xlabel("degree")
plt.ylabel("number of nodes")
plt.savefig("degree_histogram.png")
plt.show()

