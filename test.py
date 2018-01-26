import networkx as nx

G = nx.DiGraph()
G.add_node('a', demand = -5)
G.add_node('d', demand = 5)
G.add_edge('a', 'b', weight = 3, capacity = 4, multiplier = 2)
G.add_edge('a', 'c', weight = 6, capacity = 10, multiplier = 0.5)
G.add_edge('b', 'd', weight = 1, capacity = 9, multiplier = 4)
G.add_edge('c', 'd', weight = 2, capacity = 5)
flowCost, H = nx.network_simplex_generalized(G)

print(flowCost)
