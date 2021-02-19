"""
===========
Matplotlib annotations with networkx
===========

Draw a graph with matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

import networkx as nx

# Create a dataset with normally distributed feature data (for a nicer final output)
points = 20
df = pd.DataFrame(
    {
        "item": np.arange(points).astype(str),
        "feature": np.random.normal(5, 0.1, points),
    }
)

# Initialise networkX graph
G = nx.Graph()

# Generate random sparse connections
for a in range(points):
    for b in range(points):
        if a == b:
            continue
        # G.add_edge(str(a), str(b), weight=np.random.uniform(1, 10))
        G.add_edge(str(a), str(b), weight=np.random.uniform(1, 10) ** 3)

# Seed layout for reproducibility and retrieve the node positions
pos = nx.kamada_kawai_layout(G, dim=1)
df_layout = pd.DataFrame(
    {
        "item": np.array(list(pos.keys())).astype(str),
        "projection": np.array(list(pos.values())).astype(float)[:, 0],
    }
)

df = df.merge(df_layout, how="inner", on="item")

# Normalise projection according to feature
max_ = df.projection.max()
min_ = df.projection.min()
df["projection"] = (df["projection"] - min_) / (max_ - min_) * (
    df.feature.max() - df.feature.min()
) + df.feature.min()

# make pos as array of feature and projection
# df["pos"] = df.apply(lambda x: [x[1], x[2]], axis=1)
df["pos"] = np.array([df["feature"], df["projection"]]).T.tolist()


pos = {}
for index, row in df[["item", "pos"]].iterrows():
    pos[str(row[0])] = row[1]

# Generate figure
plt.figure(figsize=(10, 10))

# Define the bounding rectangles for the histogram and network
left, width = 0.1, 0.8
bottom, height = 0.1, 0.65
spacing = 0.005
rect_net = [left, bottom, width, height]
rect_histx = [left, bottom + height + spacing, width, 0.2]

# Define the network axes and labels
ax_net = plt.axes(rect_net)
# Draw the network graph
nx.draw_networkx(G, pos=pos, ax=ax_net)

ax_net.set_xlabel("feature axis")
ax_net.set_ylabel("projection axis")
ax_net.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

# Define the histogram axes and labels
ax_histx = plt.axes(rect_histx)

ax_histx.tick_params(direction="in", labelbottom=False)
n, x, _ = ax_histx.hist(df["feature"], bins=points)
ax_histx.plot(x, stats.gaussian_kde(df["feature"])(x))

plt.show()
