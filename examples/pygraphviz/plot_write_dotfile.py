"""
=============
Write Dotfile
=============


Write a dot file from a networkx graph for further processing with graphviz.

You need to have either pygraphviz or pydot for this example.

See https://networkx.github.io/documentation/latest/reference/drawing.html
"""

import networkx as nx

# This example needs Graphviz and either PyGraphviz or pydot.
# from networkx.drawing.nx_pydot import write_dot
from networkx.drawing.nx_agraph import write_dot


G = nx.grid_2d_graph(5, 5)  # 5x5 grid
write_dot(G, "grid.dot")
print("Now run: neato -Tps grid.dot >grid.ps")
