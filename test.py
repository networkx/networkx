import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

n = 8
k = 3
#G = nx.petersen_graph()
G = nx.generalized_petersen_graph(n, k)
H = nx.moebius_kantor_graph()

print( nx.is_isomorphic(G, H) )
pos = {}
for i in range(n): pos[i] = 2*np.array([np.cos(2*np.pi*i/n), np.sin(2*np.pi*i/n)])
for i in range(n): pos[n+i] = 1*np.array([np.cos(2*np.pi*i/n), np.sin(2*np.pi*i/n)])
nx.draw_networkx(G, pos, with_labels=True)


plt.show()
