import networkx as nx

# creates and builds G1 
G1 = nx.DiGraph()
nodes = [7, 6, 8, 9, 10]
G1.add_nodes_from(nodes)
edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9), (10, 7), (10, 8), (10, 9), (10, 10)]
G1.add_edges_from(edges)

# creates and builds G2 (G1 after the swap between nodes 8 and 10)
G2 = nx.DiGraph()
nodes = [7, 6, 8, 9, 10]
G2.add_nodes_from(nodes)
edges = [(6, 7), (6, 8), (6, 9), (6, 10), (9, 9),
         (10, 7), (10, 8), (10, 9), (10, 10)]
G2.add_edges_from(edges)

print(G1.nodes)
print(G2.nodes)
print(G1.nodes == G2.nodes and G1.edges == G2.edges)