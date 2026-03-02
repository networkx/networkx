"""
=======
Sampson
=======

Sampson's monastery data.

Shows how to read data from a zip file and plot multiple frames.

The data file can be found at:

- https://github.com/networkx/networkx/blob/main/examples/drawing/sampson_data.zip
"""

import zipfile

import matplotlib.pyplot as plt
import networkx as nx

# Extract the edge data for the 3 sampson-like graphs from the archive
with zipfile.ZipFile("sampson_data.zip") as zf:
    G1, G2, G3 = [
        nx.parse_edgelist(
            zf.read(f"samplike{n}.txt").decode().split("\n"), delimiter="\t"
        )
        for n in (1, 2, 3)
    ]
pos = nx.spring_layout(G3, iterations=100, seed=173)
plt.clf()

plt.subplot(221)
plt.title("samplike1")
nx.draw(G1, pos, node_size=50, with_labels=False)
plt.subplot(222)
plt.title("samplike2")
nx.draw(G2, pos, node_size=50, with_labels=False)
plt.subplot(223)
plt.title("samplike3")
nx.draw(G3, pos, node_size=50, with_labels=False)
plt.subplot(224)
plt.title("samplike1,2,3")
nx.draw(G3, pos, edgelist=list(G3.edges()), node_size=50, with_labels=False)
nx.draw_networkx_edges(G1, pos, alpha=0.25)
nx.draw_networkx_edges(G2, pos, alpha=0.25)
plt.tight_layout()
plt.show()
