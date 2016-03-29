import sys
sys.path.append('/home/mc/networkx')

import networkx as nx

G = nx.cycle_graph(3)

H = nx.Graph()
H.add_nodes_from([0,1,2,3])
H.add_edge(0,1)
H.add_edge(1,2)
H.add_edge(0,3)

r = nx.algorithms.operators.binary.rooted_product(G,H,0)
