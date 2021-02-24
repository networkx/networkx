"""
=================
Custom node icons
=================

Example of using custom icons to represent nodes with matplotlib.
"""

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import networkx as nx
import urllib.request
import io

# Image URLs for graph nodes
URLs = [
    {
        "type": "router",
        "URL": "https://www.materialui.co/materialIcons/hardware/router_black_144x144.png",
    },
    {
        "type": "switch",
        "URL": "https://www.materialui.co/materialIcons/action/dns_black_144x144.png",
    },
    {
        "type": "PC",
        "URL": "https://www.materialui.co/materialIcons/hardware/computer_black_144x144.png",
    },
]

# Import images from URLS into a collection
images = {}
for u in URLs:
    with urllib.request.urlopen(u["URL"]) as url:
        image = mpimg.imread(io.BytesIO(url.read()))
        images[u["type"]] = image

# Generate the computer network graph
G = nx.Graph()

G.add_node("router", image=images["router"])
for i in range(1, 4):
    G.add_node("switch_" + str(i), image=images["switch"])
    for j in range(1, 4):
        G.add_node("PC_" + str(i) + "_" + str(j), image=images["PC"])

G.add_edge("router", "switch_1")
G.add_edge("router", "switch_2")
G.add_edge("router", "switch_3")
for u in range(1, 4):
    for v in range(1, 4):
        G.add_edge("switch_" + str(u), "PC_" + str(u) + "_" + str(v))

pos = nx.spring_layout(G)
fig, ax = plt.subplots()
nx.draw_networkx_edges(G, pos=pos, ax=ax)

tr_figure = ax.transData.transform
tr_axes = fig.transFigure.inverted().transform

# Draw the images on top of the graph
icon_size = 0.05
icon_center = icon_size / 2.0

# Add the respective image to each node
for n in G.nodes:
    xf, yf = tr_figure(pos[n])
    xa, ya = tr_axes((xf, yf))
    a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
    a.imshow(G.nodes[n]["image"])
    a.axis("off")
plt.show()
