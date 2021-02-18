"""
===========
Matplotlib annotations with networkx
===========

Draw a graph with matplotlib.
"""

# import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import numpy as np

df = pd.DataFrame(
    {
        "item": np.array(["a", "b", "c", "d", "e", "f"]).astype(str),
        "feature": np.array([1, 2, 1.5, 3, 0.5, 3.2]).astype(float),
    }
)

G = nx.Graph()

G.add_edge("a", "b", weight=0.6)
G.add_edge("a", "c", weight=0.2)
G.add_edge("c", "d", weight=0.1)
G.add_edge("c", "e", weight=0.7)
G.add_edge("c", "f", weight=0.9)
G.add_edge("a", "d", weight=0.3)

pos = nx.kamada_kawai_layout(G, dim=1)  # Seed layout for reproducibility
# nx.draw(G, pos=pos)
df_layout = pd.DataFrame(
    {
        "item": np.array(list(pos.keys())).astype(str),
        "projection": np.array(list(pos.values())).astype(float)[:, 0],
    }
)
df = df.merge(df_layout, how="inner", on="item")
print(df)
# normalise projection according to feature
max_ = df.projection.max()
min_ = df.projection.min()
df["projection"] = (df["projection"] - min_) / (max_ - min_) * (
    df.feature.max() - df.feature.min()
) + df.feature.min()
print(df)

pos = df[["feature", "projection"]].values.tolist()
print(pos)

# nx.draw(G, pos=pos)
# plt.show()
