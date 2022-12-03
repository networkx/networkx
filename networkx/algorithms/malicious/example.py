import networkx as nx

G = nx.DiGraph()
nodes = range(1, 12)
G.add_nodes_from(nodes)
edges = [(edge, edge+1) for edge in range(1, 11)]
edges.append((7,11))
edges.append((10, 7))
print(edges)
G.add_edges_from(edges)

print(G)
nx.draw(G)

