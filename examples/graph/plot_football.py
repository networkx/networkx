"""
========
Football
========

Load football network in GML format and compute some network statistics.
Data provided by authors of [1]_

Shows how to unpack a zipped GML file and load it into a NetworkX graph.
This example uses the pathlib library for filename manipulation.

The data file can be found at:

- https://public.websites.umich.edu/~mejn/netdata/football.zip

.. [1] M. Girvan and M. E. J. Newman,
       Community structure in social and biological networks,
       Proc. Natl. Acad. Sci. USA 99, 7821-7826 (2002).
       https://arxiv.org/abs/cond-mat/0112110
"""

from pathlib import Path
import zipfile

import matplotlib.pyplot as plt
import networkx as nx

with zipfile.ZipFile(Path.cwd() / "football.zip") as zf:  # zipfile object
    txt = zf.read("football.txt").decode()  # read info file
    gml = zf.read("football.gml").decode()  # read gml data

# throw away bogus first line with # from mejn files
gml = gml.split("\n")[1:]
G = nx.parse_gml(gml)  # parse gml data

print(txt)
# print degree for each team - number of games
for n, d in G.degree():
    print(f"{n:20} {d:2}")

# Extract conference data from the text
conf_data = txt.split("\n\n")[1].split("\n")

# Color nodes by primary color of conference champions (from Wikipedia)
# fmt: off
champ_clrs = [
    "#782F40", "#F47321", "#00274C", "#841617", "#FDB913", "#AE9142", "#00B140",
    "#1E4D2B", "#4b2e83", "#0021A5", "#343636", "#B1B3B3"
]
# fmt: on
conf_mapping = {}
for line, clr in zip(conf_data, champ_clrs):
    conf_key, conf_name = line.split("=")
    conf_mapping[int(conf_key)] = {"name": conf_name.strip(), "color": clr}

pos = nx.spring_layout(G, seed=1969)  # Seed for reproducible layout
fig, ax = plt.subplots(figsize=(10, 6))

# Draw nodes for each conference separately to populate handles for a legend
opts = {"node_size": 50, "linewidths": 0}
for conf, data in conf_mapping.items():
    nodes = [n for n, c in G.nodes(data="value") if c == conf]
    label = data["name"]
    color = data["color"]
    nx.draw_networkx_nodes(
        G, pos=pos, ax=ax, nodelist=nodes, label=label, node_color=color, **opts
    )
ax.legend(loc=8, ncols=6, bbox_to_anchor=(0.5, -0.15))

# Draw edges
nx.draw_networkx_edges(G, pos=pos, ax=ax, width=0.1)

ax.set_axis_off()
fig.tight_layout()
plt.show()
