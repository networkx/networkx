"""
===============
Degree Sequence
===============

Random graph from given degree sequence.
"""

from pprint import pprint
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
print(f"Degree sequence of G identical to z: {degree_sequence == z}")

print("\nDegree histogram")
deg_hist = dict(enumerate(nx.degree_histogram(G)))
print("degree: #nodes")
pprint(deg_hist, width=10)

pos = nx.spring_layout(G, seed=seed)  # Seed layout for reproducibility
nx.draw(G, pos=pos)
plt.show()
