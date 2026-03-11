"""
======================
Read and write graphs.
======================

Read and write graphs.
"""

import io
import matplotlib.pyplot as plt
import networkx as nx

G = nx.grid_2d_graph(5, 5)  # 5x5 grid

# Use BytesIO as a virtual file handle.
# Replace with: `with open(<filename>, "wb") as fh:` to save to disk
fh = io.BytesIO()
# write edgelist to file
nx.write_edgelist(G, path=fh, delimiter=":")
# View file contents
print(fh.getvalue().decode())
# read edgelist from file
fh.seek(0)
H = nx.read_edgelist(path=fh, delimiter=":")

pos = nx.spring_layout(H, seed=200)
nx.draw(H, pos)
plt.show()
