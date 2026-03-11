"""
==========
Properties
==========

Compute some network properties for the lollipop graph.
"""

import matplotlib.pyplot as plt
import networkx as nx
from pprint import pprint

G = nx.lollipop_graph(4, 6)

print("Shortest path length between all node pairs:")
print("{source node: {target node: path length}")
path_lengths = dict(nx.all_pairs_shortest_path_length(G))
pprint(path_lengths)

print(f"average shortest path length {sum(pathlengths) / len(pathlengths)}")

# histogram of path lengths
dist = {}
for p in pathlengths:
    if p in dist:
        dist[p] += 1
    else:
        dist[p] = 1

print()
print("length #paths")
verts = dist.keys()
for d in sorted(verts):
    print(f"{d} {dist[d]}")

print(f"radius: {nx.radius(G)}")
print(f"diameter: {nx.diameter(G)}")
print(f"eccentricity: {nx.eccentricity(G)}")
print(f"center: {nx.center(G)}")
print(f"periphery: {nx.periphery(G)}")
print(f"density: {nx.density(G)}")

pos = nx.spring_layout(G, seed=3068)  # Seed layout for reproducibility
nx.draw(G, pos=pos, with_labels=True)
plt.show()
