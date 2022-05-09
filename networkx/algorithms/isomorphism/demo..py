import networkx as nx
import matplotlib.pyplot as plt

# G1 = nx.barbell_graph(5, 4)
# G2 = nx.barbell_graph(5, 4)

G1 = nx.Graph()
G1.add_edge(0, 1)
G1.add_edge(1, 2)
G1.add_edge(0, 3)
G1.add_edge(0, 2)

G2 = nx.Graph()
G2.add_edge(2, 3)
G2.add_edge(2, 1)
G2.add_edge(2, 0)
G2.add_edge(1, 0)

# nx.draw(G1, with_labels=True)
# plt.show()
# nx.draw(G2, with_labels=True)
# plt.show()

isomorphic = nx.is_isomorphic(G1, G2)
print(isomorphic)

