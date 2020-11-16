"""
=========
GeoPandas
=========

This example shows how to read a shapefile with GeoPandas,
and convert it to a NetworkX graph....
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx


# %%
# TODO

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
world.plot()
plt.show()
