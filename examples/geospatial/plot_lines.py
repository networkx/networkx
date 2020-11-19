"""
=====
Graphs from a set of lines
=====

This example shows how to build a graph from a set of geographic lines 
(sometimes called "linestrings") using PySAL and geopandas. We'll plot
some streets in Tempe, Arizona, as well as the graph formed from the segments.  
"""

from libpysal import weights, examples
from contextily import add_basemap
import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import numpy

# read in example data online
filepath = examples.get_path("streets.shp")
tempe = geopandas.read_file(filepath).to_crs(epsg=3857)

coordinates = numpy.column_stack((tempe.centroid.x, tempe.centroid.y))

# construct the graph
w_graph = weights.Queen.from_dataframe(tempe)

# convert the graph to networkx
graph = w_graph.to_networkx()


# merge the nodes back to their positions
positions = dict(zip(graph.nodes, coordinates))


# plot
f, ax = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)
tempe.plot(color="k", ax=ax[0])
for i, facet in enumerate(ax):
    add_basemap(facet)
    facet.set_title(("Streets", "Graph")[i])
nx.draw(graph, positions, ax=ax[1], node_size=5)
plt.show()
