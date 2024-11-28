import networkx as nx
G = nx.Graph()
#G = nx.Graph([(0, 1), (1, 2), (3, 4)])
# wrong way - will raise RuntimeError
# G.add_nodes_from(n + 1 for n in G.nodes)
# correct way
G.add_nodes_from(list(n + 1 for n in G.nodes))
G.add_nodes_from([(4, {"color": "red"}), (5, {"color": "green"})])
