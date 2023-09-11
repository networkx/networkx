"""
================
Visibility Graph
================

Visibility Graph constructed from a time series
"""
from matplotlib import pyplot

import networkx as nx

time_series = [0, 2, 1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 3, 4, 0]
# or
# import random
# time_series = [random.randint(1,10) for i in range(10)]

g = nx.visibility_graph(time_series)

labels = nx.get_node_attributes(g, "value")

# a layout emphasizing the line-of-sight connectivity
pos = {x: (x, 0) for x in range(len(time_series))}
nx.draw_networkx_nodes(g, pos)
nx.draw_networkx_labels(g, pos, labels=labels)
nx.draw_networkx_edges(
    g,
    pos,
    arrows=True,
    arrowstyle="->",
    arrowsize=10,
    connectionstyle="arc3,rad=-1.57079632679",
)
pyplot.show()

# a layout showcasing the time series values
pos = {i: (i, v) for i, v in enumerate(time_series)}
nx.draw_networkx_nodes(g, pos)
nx.draw_networkx_labels(g, pos, labels=labels)
nx.draw_networkx_edges(g, pos, arrows=True, arrowstyle="->", arrowsize=10)
pyplot.show()
