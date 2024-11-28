import networkx as nx
G = nx.Graph(name="my graph")
e = [(1, 2), (2, 3), (3, 4)]  # list of edges
G = nx.Graph(e)

G = nx.Graph(e, day="Friday")
G.graph
{'day': 'Friday'}
H = nx.path_graph(10)
G.add_nodes_from(H)
H.add_nodes_from(G.nodes(data=True))
H.nodes[1]