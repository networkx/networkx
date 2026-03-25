"""
==========
Properties
==========

Compute some network properties for the lollipop graph.
"""

from collections import Counter
import itertools
import matplotlib.pyplot as plt
import networkx as nx
from pprint import pprint

G = nx.lollipop_graph(4, 6)

# %%
# A quick summary of basic properties is available via `nx.describe`
nx.describe(G)
print(f"density: {nx.density(G)}")

print("\nShortest path length between all node pairs:")
print("  {source node: {target node: path length}")
path_lengths = dict(nx.all_pairs_shortest_path_length(G))
pprint(path_lengths)

print(f"\naverage shortest path length {nx.average_shortest_path_length(G)}")

# %%
# Histogram of path lengths - note that this counts each path twice: from
# src -> tgt and tgt -> src.
print("\nDistribution of shortest path lengths")
path_length_distribution = Counter(
    itertools.chain.from_iterable(t.values() for t in path_lengths.values())
)
pprint({pl: num // 2 for pl, num in path_length_distribution.items()})

# %%
# Basic distance measures. In some cases it is possible to pass in pre-computed
# eccentricity values to speed up subsequent computations.
# Re-using computed values may significantly improve computation times for
# larger graphs


eccentricity = nx.eccentricity(G)
print(f"\neccentricity: {eccentricity}")
print(f"radius: {nx.radius(G, e=eccentricity)}")
print(f"diameter: {nx.diameter(G, e=eccentricity)}")
print(f"center: {nx.center(G, e=eccentricity)}")
print(f"periphery: {nx.periphery(G, e=eccentricity)}")

pos = nx.spring_layout(G, seed=3068)  # Seed layout for reproducibility
nx.draw(G, pos=pos, with_labels=True)
plt.show()
