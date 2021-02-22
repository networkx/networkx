"""
===========
Matplotlib composite plot of feature distribution and network topology
===========

Draw a composite plot on matplotlib showing distribution of nodes' features and the network topology at the same time.

This can be useful when you have a dataset with feature information for different items and some links between different
items.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats

import networkx as nx

# set seed for the toy example
np.random.seed(4242)

# Create a dataset with normally distributed feature data (for a nicer final output)
points = 50
df = pd.DataFrame(
    {
        "item": np.arange(points).astype(str),
        "feature": np.random.normal(0, 0.05, points),
    }
)

# Initialise networkX graph
G = nx.Graph()

# Generate dummy graph edges
for a in range(points):
    for b in np.random.choice(range(points), int(points / 10), replace=False):
        if a == b:
            continue
        # G.add_edge(str(a), str(b), weight=np.random.uniform(1, 10))
        G.add_edge(str(a), str(b), weight=np.random.uniform(1, 10) ** 3)

# generate a layout for the graph in 1 dimension (the projection based on graph topology)
pos = nx.kamada_kawai_layout(G, dim=1)
df_layout = pd.DataFrame(
    {
        "item": np.array(list(pos.keys())).astype(str),
        "projection": np.array(list(pos.values())).astype(float)[:, 0],
    }
)

# join the projections with the features dataframe
df = df.merge(df_layout, how="inner", on="item")

# Normalise projection according to feature
max_proj = df.projection.max()
min_proj = df.projection.min()

df["projection"] = (df["projection"] - min_proj) / (max_proj - min_proj) * (
    df.feature.max() - df.feature.min()
) + df.feature.min()

# make pos as array of feature and projection
df["pos"] = np.array([df["feature"], df["projection"]]).T.tolist()

# create a dict required for networkx.draw_networkx()
pos = {}
for index, row in df[["item", "pos"]].iterrows():
    pos[str(row[0])] = row[1]

# Generate a new figure
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

# find plot bounds for scaling everything correctly
diff_feature = df.feature.max() - df.feature.min()
max_feature = df.feature.max() + diff_feature * 0.05
min_feature = df.feature.min() - diff_feature * 0.05

# draw translucent vlines linking nodes and histogram positions
for index, row in df[["feature"]].iterrows():
    ax_net.axvline(row[0], alpha=0.2)

# add labels and ticks
ax_net.set_xlabel("feature axis")
ax_net.set_ylabel("projection axis")
ax_net.set_xlim(min_feature, max_feature)
ax_net.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)

# Define the histogram axes and labels
ax_histx = plt.axes(rect_histx)

# plot feature histogram
n, x, _ = ax_histx.hist(df["feature"], bins=100)
# plot density estimate for the same
ax_histx.plot(x, stats.gaussian_kde(df["feature"])(x))
ax_histx.set_xlim(min_feature, max_feature)
ax_histx.tick_params(left=True, bottom=True)

plt.show()
