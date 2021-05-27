"""
=================
Custom node icons
=================

Example of using custom icons to represent nodes with matplotlib.
"""

import matplotlib.pyplot as plt
import networkx as nx
import PIL
import urllib.request

# Image URLs for graph nodes
icon_urls = {
    "router": "https://www.materialui.co/materialIcons/hardware/router_black_144x144.png",
    "switch": "https://www.materialui.co/materialIcons/action/dns_black_144x144.png",
    "PC": "https://www.materialui.co/materialIcons/hardware/computer_black_144x144.png",
}

# Load images from web
images = {
    k: PIL.Image.open(urllib.request.urlopen(url)) for k, url in icon_urls.items()
}

# Generate the computer network graph
G = nx.Graph()

G.add_node("router", image=images["router"])
for i in range(1, 4):
    G.add_node(f"switch_{i}", image=images["switch"])
    for j in range(1, 4):
        G.add_node("PC_" + str(i) + "_" + str(j), image=images["PC"])

G.add_edge("router", "switch_1")
G.add_edge("router", "switch_2")
G.add_edge("router", "switch_3")
for u in range(1, 4):
    for v in range(1, 4):
        G.add_edge("switch_" + str(u), "PC_" + str(u) + "_" + str(v))

# get layout and draw edges
pos = nx.spring_layout(G)
fig, ax = plt.subplots()
nx.draw_networkx_edges(G, pos=pos, ax=ax, min_source_margin=15, min_target_margin=15)

# Transform from data coordinates (scaled between xlim and ylim) to display coordinates
tr_figure = ax.transData.transform
# Transform from display to figure coordinates
tr_axes = fig.transFigure.inverted().transform

# Select the size of the image (relative to the X axis)
icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
icon_center = icon_size / 2.0

# Add the respective image to each node
for n in G.nodes:
    xf, yf = tr_figure(pos[n])
    xa, ya = tr_axes((xf, yf))
    # get overlapped axes and plot icon
    a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
    a.imshow(G.nodes[n]["image"])
    a.axis("off")
plt.show()
