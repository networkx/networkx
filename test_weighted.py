import networkx as nx

G = nx.Graph()
G.add_edge(0, 1, weight=0.6)
G.add_edge(0, 2, weight=0.222222)
G.add_edge(2, 3, weight=0.1)
G.add_edge(2, 4, weight=0.762)
G.add_edge(2, 5, weight=0.9)
G.add_edge(1, 5, weight=0.3)

print("weighted: ", dict(nx.eccentricity(G)))
print("weighted: ", nx.algorithms.distance_measures._extrema_bounding(G))

G = nx.Graph()
G.add_edge(0, 1)
G.add_edge(0, 2)
G.add_edge(2, 3)
G.add_edge(2, 4)
G.add_edge(2, 5)
G.add_edge(1, 5)

print("unweighted: ", dict(nx.eccentricity(G)))
