"""
===============
Degree Sequence
===============

Random graph from given degree sequence.
"""
import matplotlib.pyplot as plt
from networkx import nx

z = [5, 3, 3, 3, 3, 2, 2, 2, 1, 1, 1]
print(nx.is_graphical(z))

print("Configuration model")
G = nx.configuration_model(z)  # configuration model
degree_sequence = [d for n, d in G.degree()]  # degree sequence
print(f"Degree sequence {degree_sequence}")
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

nx.draw(G)
plt.show()
