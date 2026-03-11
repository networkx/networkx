"""
===============
Degree Sequence
===============

Random graph from given degree sequence.
"""

import matplotlib.pyplot as plt
import networkx as nx

# Specify seed for reproducibility
seed = 668273

z = [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1]
print(f"Sequence {z} is a valid degree sequence: {nx.is_graphical(z)}")

G = nx.configuration_model(z, seed=seed)
degree_sequence = [d for _, d in G.degree()]

# The degree sequence for the random graph computed using configuration_model
# should match the degree sequence used to generate it
print(f"Degree sequence {degree_sequence} identical to z: {degree_sequence == z}")
print("Degree histogram")
hist = {}
for d in degree_sequence:
    if d in hist:
        hist[d] += 1
    else:
        hist[d] = 1
print("degree #nodes")
for d in hist:
    print(f"{d:4} {hist[d]:6}")

pos = nx.spring_layout(G, seed=seed)  # Seed layout for reproducibility
nx.draw(G, pos=pos)
plt.show()
