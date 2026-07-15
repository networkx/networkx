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

# %%
# Note that the original graph `G` had tuples as nodes. In order to recover
# the original node type, the data read from file must be properly interpreted
# using the `nodetype` kwarg
H = nx.read_edgelist(
    path=fh,
    # Convert from a string back to a tuple-of-int
    nodetype=lambda s: tuple(int(v) for v in s[1:-1].split(",")),
    delimiter=":",
)

nx.draw(H, pos={n: n for n in H})
plt.show()
