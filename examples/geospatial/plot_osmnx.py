"""
=====
OSMnx
=====

This example shows how to read a shapefile with OSMnx
and convert it to a NetworkX graph....
"""

import osmnx as ox
import networkx as nx

# %%
# TODO

G = ox.graph_from_point((37.79, -122.41), dist=750, network_type="all")
ox.plot_graph(G)
