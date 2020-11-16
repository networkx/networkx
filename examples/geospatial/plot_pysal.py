"""
=====
PySAL
=====

This example shows how to read a shapefile with PySAL,
the Python Spatial Analysis Library, and convert it
to a NetworkX graph....
"""

import libpysal
import geopandas as gpd
import mapclassify as mc
import matplotlib.pyplot as plt
import networkx as nx

# %%
# TODO

columbus = gpd.read_file(libpysal.examples.get_path("columbus.shp"))
q5 = mc.Quantiles(columbus.CRIME, k=5)
q5.plot(columbus, axis_on=False, cmap="Blues")
plt.show()
